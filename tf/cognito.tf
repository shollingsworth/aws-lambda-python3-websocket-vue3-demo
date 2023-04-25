resource "aws_cognito_user_pool" "idp" {
  name                     = local.prefix
  auto_verified_attributes = ["email"]
}

resource "aws_cognito_user_pool_domain" "idp" {
  domain       = local.prefix
  user_pool_id = aws_cognito_user_pool.idp.id
}

resource "aws_cognito_identity_provider" "google" {
  user_pool_id  = aws_cognito_user_pool.idp.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    authorize_scopes              = "email"
    client_id                     = data.aws_kms_secrets.secrets.plaintext["client_id"]
    client_secret                 = data.aws_kms_secrets.secrets.plaintext["client_secret"]
    attributes_url                = "https://people.googleapis.com/v1/people/me?personFields="
    attributes_url_add_attributes = "true"
    authorize_url                 = "https://accounts.google.com/o/oauth2/v2/auth"
    oidc_issuer                   = "https://accounts.google.com"
    token_request_method          = "POST"
    token_url                     = "https://www.googleapis.com/oauth2/v4/token"
  }

  attribute_mapping = {
    email    = "email"
    username = "sub"
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name         = "${local.prefix}-client"
  user_pool_id = aws_cognito_user_pool.idp.id
  callback_urls = [
    "https://${local.stages["prod"]}",
    "https://${local.stages["dev"]}",
    "http://localhost:8080",
  ]
  logout_urls = [
    "https://${local.stages["prod"]}",
    "https://${local.stages["dev"]}",
    "http://localhost:8080",
  ]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid"]
  supported_identity_providers         = ["Google"]
}

resource "aws_ssm_parameter" "cognito_user_pool_id" {
  name  = "/${local.prefix}/cognito_user_pool_id"
  value = aws_cognito_user_pool.idp.id
  type  = "String"
}

resource "aws_ssm_parameter" "cognito_user_pool_client_id" {
  name  = "/${local.prefix}/cognito_user_pool_client_id"
  type  = "String"
  value = aws_cognito_user_pool_client.client.id
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.idp.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.client.id
}

output "cognito_domain" {
  value = "https://${aws_cognito_user_pool_domain.idp.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
}

output "cognito_redirect_uri" {
  value = "https://${aws_cognito_user_pool_domain.idp.domain}.auth.${data.aws_region.current.name}.amazoncognito.com/oauth2/idpresponse"
}
