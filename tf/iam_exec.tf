data "aws_iam_policy_document" "assume-execrole" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "policy-execrole" {
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
      "dynamodb:Update*",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:PutItem",
      "dynamodb:Get*",
      "dynamodb:Delete*",
      "dynamodb:BatchWrite*",
      "dynamodb:BatchGet*",
    ]
    resources = [
      aws_dynamodb_table.dyn["prod"].arn,
      aws_dynamodb_table.dyn["dev"].arn,
    ]
  }
}

resource "aws_iam_role" "execrole" {
  assume_role_policy = data.aws_iam_policy_document.assume-execrole.json
  name               = "${local.prefix}-execrole"
}
