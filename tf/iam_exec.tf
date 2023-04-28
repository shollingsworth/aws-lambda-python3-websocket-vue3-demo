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
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]
    resources = [
      aws_dynamodb_table.dyn["prod"].arn,
      aws_dynamodb_table.dyn["dev"].arn,
      aws_dynamodb_table.dyn["prod"].stream_arn,
      aws_dynamodb_table.dyn["dev"].stream_arn,
    ]
  }

  statement {
    # allow this to post to websockets
    actions = [
      "execute-api:ManageConnections"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    # allow this to post to websockets
    actions = [
      "sns:Publish",
    ]
    resources = [
      aws_sns_topic.user_updates["prod"].arn,
      aws_sns_topic.user_updates["dev"].arn,
    ]
  }
}

resource "aws_iam_role" "execrole" {
  assume_role_policy = data.aws_iam_policy_document.assume-execrole.json
  inline_policy {
    name   = "policy-execrole"
    policy = data.aws_iam_policy_document.policy-execrole.json
  }
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
  name = "${local.prefix}-execrole"
}

resource "aws_ssm_parameter" "execrole" {
  name  = "/${local.prefix}/execrole"
  type  = "String"
  value = aws_iam_role.execrole.arn
}

output "exec_role" {
  value = aws_iam_role.execrole.arn
}
