resource "aws_sns_topic" "user_updates" {
  for_each                    = local.stages
  name_prefix                 = "${local.prefix}-${each.key}"
}

resource "aws_ssm_parameter" "sns_topic_arn" {
  for_each                    = local.stages
  name  = "/${local.prefix}/${each.key}/sns"
  value = aws_sns_topic.user_updates[each.key].arn
  type  = "String"
}

output "sns_topic_arn" {
  value = {
    for k, v in aws_sns_topic.user_updates : k => v.arn
  }
}
