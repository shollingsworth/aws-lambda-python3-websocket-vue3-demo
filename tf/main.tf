provider "aws" {
  region = "${local.region}"
  default_tags {
    tags = {
      source-control = "https://github.com/${local.repo_owner}/${local.repo_name}"
    }
  }
}

provider "aws" {
  alias = "useast"
  # static, has to be for cloudfront ssl certs
  region = "us-east-1"
  default_tags {
    tags = {
      source-control = "https://github.com/${local.repo_owner}/${local.repo_name}"
    }
  }
}

## Change these backend values to fit your needs. You can keep a separate TF repo just for storing you
## terraform states, see: https://gist.github.com/shollingsworth/1bb7b78e5fa20bfe55a28b91904b42ae
## Or you can just remove this block all together to store it locally, be sure to exclude the state from your .gitignore file
## if you do so.
terraform {
  backend "s3" {
    bucket         = "shollingsworth-terraform-tfstate"
    dynamodb_table = "shollingsworth-terraform-state-lock"
    key            = "sh-ws-demo/terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
  }
}
