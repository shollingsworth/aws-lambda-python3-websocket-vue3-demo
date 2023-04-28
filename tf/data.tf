## change prefix in ../config.json to fit your needs
locals {
  jdata = jsondecode(file("${path.module}/../config.json"))
  prefix = local.jdata.prefix
  region = local.jdata.region
  repo_name = local.jdata.repo_name
  repo_owner = local.jdata.repo_owner
  domain = local.jdata.domain
  stages = {
    "dev": "${local.prefix}-dev.${local.domain}",
    "prod": "${local.prefix}.${local.domain}"
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_route53_zone" "domain" {
    name = local.domain
}
