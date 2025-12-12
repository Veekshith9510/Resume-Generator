# We assume the zip file is created by the CI/CD pipeline or manually
# For local dev, we can verify if it exists, but for now we'll point to a path.
# In the GitHub Actions workflow, we saw it moves `backend_lambda.zip` to the terraform dir.

resource "aws_lambda_function" "api" {
  filename      = "backend_lambda.zip"
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.lambda_role.arn
  handler       = "main.handler" # Assuming main.py and a handler function like 'handler' or using Mangum
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 256

  source_code_hash = fileexists("backend_lambda.zip") ? filebase64sha256("backend_lambda.zip") : null

  environment {
    variables = {
      GEMINI_SECRET_NAME = aws_secretsmanager_secret.gemini_api_key.name
      RESUME_BUCKET      = aws_s3_bucket.resumes.id
      OUTPUT_BUCKET      = aws_s3_bucket.generated_resumes.id
      DDB_TABLE          = aws_dynamodb_table.resumes.name
    }
  }
}
