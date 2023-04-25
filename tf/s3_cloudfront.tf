#############################################################
# Bucket
#############################################################

resource "aws_s3_bucket" "cf-bucket" {
  for_each      = local.stages
  bucket        = "${local.prefix}-${each.key}-s3cf"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "cf-bucket" {
  for_each = local.stages
  bucket   = aws_s3_bucket.cf-bucket[each.key].id
  versioning_configuration {
    status = "Disabled"
  }
}

# aws_s3_bucket_website_configuration.web["dev"] will be destroyed
# (because aws_s3_bucket_website_configuration.web is not in configuration)
resource "aws_s3_bucket_website_configuration" "web" {
  for_each = local.stages
  bucket   = aws_s3_bucket.cf-bucket[each.key].id

  error_document {
    key = "error.html"
  }

  index_document {
    suffix = "index.html"
  }
}

#############################################################
# Cert
#############################################################
resource "aws_acm_certificate" "cert" {
  provider    = aws.useast
  domain_name = "*.${local.domain}"
  subject_alternative_names = [
    "${local.stages["dev"]}",
    "${local.stages["prod"]}",
  ]
  validation_method = "DNS"
}

resource "aws_route53_record" "cert" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }


  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.domain.zone_id
}


resource "aws_acm_certificate_validation" "cert" {
  provider                = aws.useast
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert : record.fqdn]
}

#############################################################
# Cloudfront
#############################################################
resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  for_each = local.stages
  comment  = "${each.value} Allow CloudFront to reach my bucket"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  for_each = local.stages
  comment  = "CDN for ${each.value}"
  aliases = [
    each.value,
  ]

  custom_error_response {
    error_caching_min_ttl = 10
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
  }
  origin {
    domain_name         = aws_s3_bucket.cf-bucket[each.key].bucket_regional_domain_name
    origin_id           = each.value
    connection_attempts = 3
    connection_timeout  = 10
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin_access_identity[each.key].cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # logging_config {
  #   include_cookies = false
  #   bucket          = "mylogs.s3.amazonaws.com"
  #   prefix          = "myprefix"
  # }

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = each.value

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_200"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations = [
        "CA",
        "DE",
        "GB",
        "IN",
        "IR",
        "US",
      ]
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cert.arn
    minimum_protocol_version = "TLSv1.2_2019"
    ssl_support_method       = "sni-only"
  }
}


#############################################################
# Cloudfront bucket tie in
#############################################################
data "aws_iam_policy_document" "cf-bucket" {
  for_each = local.stages
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.cf-bucket[each.key].arn}/*"]
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.origin_access_identity[each.key].iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cf-bucket" {
  for_each = local.stages
  bucket   = aws_s3_bucket.cf-bucket[each.key].id
  policy   = data.aws_iam_policy_document.cf-bucket[each.key].json
}

resource "aws_route53_record" "r53_dom" {
  for_each = local.stages
  name     = each.value
  type     = "A"
  zone_id  = data.aws_route53_zone.domain.zone_id

  alias {
    evaluate_target_health = false
    name                   = aws_cloudfront_distribution.s3_distribution[each.key].domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution[each.key].hosted_zone_id
  }
}
