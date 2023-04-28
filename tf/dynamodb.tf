resource "aws_dynamodb_table" "dyn" {
  for_each                    = local.stages
  name                        = "${local.prefix}-${each.key}"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false
  hash_key                    = "type"
  range_key                   = "key"
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "key"
    type = "S"
  }
  attribute {
    name = "type"
    type = "S"
  }
}

resource "aws_ssm_parameter" "dynamodb_table" {
  for_each                    = local.stages
  name  = "/${local.prefix}/${each.key}/dynamodb_stream_arn"
  value = aws_dynamodb_table.dyn[each.key].stream_arn
  type  = "String"
}

resource "aws_ssm_parameter" "dynamodb_table_name" {
  for_each                    = local.stages
  name  = "/${local.prefix}/${each.key}/dynamodb_name"
  value = aws_dynamodb_table.dyn[each.key].name
  type  = "String"
}
