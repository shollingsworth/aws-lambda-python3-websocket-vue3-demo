resource "aws_dynamodb_table" "dyn" {
  for_each                    = local.stages
  name                        = "${local.prefix}-${each.key}"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false
  hash_key                    = "type"
  range_key                   = "key"

  attribute {
    name = "key"
    type = "S"
  }
  attribute {
    name = "type"
    type = "S"
  }
}
