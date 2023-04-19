## change prefix in ../config.json to fit your needs
locals {
  jdata = jsondecode(file("${path.module}/../config.json"))
  prefix = local.jdata.prefix
  source = local.jdata.source
  domain = local.jdata.domain
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_route53_zone" "domain" {
    name = local.domain
}
