######################
# uncomment if doesn't exist
######################
# resource "aws_iam_openid_connect_provider" "github" {
#   url             = "https://token.actions.githubusercontent.com"
#   client_id_list  = ["sts.amazonaws.com"]
#   thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
# }

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "AWS"
      identifiers = [
        format(
          "arn:aws:iam::%s:root",
          data.aws_caller_identity.current.account_id
        )
      ]
    }
  }

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type = "Federated"
      identifiers = [
        # uncomment if doesn't exist
        # aws_iam_openid_connect_provider.github.arn
        data.aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values = [
        "sts.amazonaws.com",
      ]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${local.repo_owner}/${local.repo_name}:*"]
    }
  }
}



data "aws_iam_policy_document" "github-actions-policy" {

  statement {
    actions = [
      "ssm:GetParameters",
      "ssm:GetParameter",
    ]
    resources = [
      format("arn:aws:ssm:%s:%s:parameter/%s/*",
        data.aws_region.current.name,
        data.aws_caller_identity.current.account_id,
        local.prefix,
      ),
    ]
  }

  statement {
    actions = [
      "s3:PutObject",
      "s3:ListBucket",
      "s3:GetObject",
      "s3:DeleteObject",
    ]

    resources = [
      aws_s3_bucket.cf-bucket["prod"].arn,
      aws_s3_bucket.cf-bucket["dev"].arn,
      "${aws_s3_bucket.cf-bucket["dev"].arn}/*",
      "${aws_s3_bucket.cf-bucket["prod"].arn}/*",
    ]
  }

  statement {
    actions = [
      "cloudfront:CreateInvalidation",
    ]
    resources = [
      aws_cloudfront_distribution.s3_distribution["dev"].arn,
      aws_cloudfront_distribution.s3_distribution["prod"].arn,
    ]
  }

  statement {
    actions = [
      "cloudfront:ListDistributions",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${local.prefix}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy.json
  inline_policy {
    name   = "github-actions-policy"
    policy = data.aws_iam_policy_document.github-actions-policy.json
  }
}
