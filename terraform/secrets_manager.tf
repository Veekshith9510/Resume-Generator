resource "aws_secretsmanager_secret" "gemini_api_key" {
  name        = "gemini_api_key_v3" # Using v3 to avoid conflict if v2 exists
  description = "API Key for Google Gemini"
}

# The actual secret value will be managed outside of Terraform or via the workflow
# to avoid committing it to state if possible, or we can create a placeholder version.
resource "aws_secretsmanager_secret_version" "gemini_api_key_initial" {
  secret_id     = aws_secretsmanager_secret.gemini_api_key.id
  secret_string = "{\"GEMINI_API_KEY\":\"placeholder\"}"
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}
