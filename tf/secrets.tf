# existing kms key, change to fit needs
data "aws_kms_alias" "general" {
  name = "alias/general"
}

# to get encrypted value
# aws --region us-east-2 kms encrypt --plaintext fileb://secret.txt --key-id alias/general --query CiphertextBlob --output text | tee
# or
# aws --region us-east-2 kms encrypt --plaintext "$(echo "secret" | base64 -w0)" --key-id alias/general --query CiphertextBlob --output text | tee
# to get secret value
# aws kms decrypt --ciphertext-blob "<payload>" --query Plaintext --output text | base64 -d
data "aws_kms_secrets" "secrets" {
    secret {
      # google client it
      name = "client_id"
      payload = "AQICAHhvAAO5zGCmqYILw7OPZcdUsHr0BeS9hJ32XbS25aFOzgHOGrV73ypOGW6aNxIzU6IFAAAAqjCBpwYJKoZIhvcNAQcGoIGZMIGWAgEAMIGQBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDO27s/erAKNgTrrk5QIBEIBjpNpMmQCOpqpPIFeHs9C1C1kRimlyhn1ubF9pi4PLlLpCBSsUxzWWqyBBjx6gFwN8U7o1zoZacYnVR00tu3HJ1VO8uZLTvaAkBaoBiD279wfRHCc2A85JSdevF5g/OqlhogP3"
    }

    secret {
        # google secret
        name = "client_secret"
        payload = "AQICAHhvAAO5zGCmqYILw7OPZcdUsHr0BeS9hJ32XbS25aFOzgFl+TChcJ6PdCaiQ4snSCpbAAAAgTB/BgkqhkiG9w0BBwagcjBwAgEAMGsGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMoKNujj1mGhuX6RphAgEQgD5okf2gXj+8U5h4tGCuSu4QYYZUUUOFe9422gp6hZ7NOczx0Fl1EDQG+Pbvr9kjcPFqq9veJWzIkR8gn/PTAA=="
    }
}

