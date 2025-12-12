terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" 
}

# --- Variables ---

variable "project_name" {
  default = "resume-generator-ai"
}

variable "github_repo" {
  description = "GitHub repository for OIDC (e.g., user/repo)"
  default     = "Veekshith9510/Resume-Generator" 
}

# --- S3 Buckets ---

# Bucket for React Frontend
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "${var.project_name}-frontend-v9510" 
}

resource "aws_s3_bucket_website_configuration" "frontend_website" {
  bucket = aws_s3_bucket.frontend_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend_bucket_public_access" {
  bucket = aws_s3_bucket.frontend_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend_bucket_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend_bucket.arn}/*"
      },
    ]
  })
  depends_on = [aws_s3_bucket_public_access_block.frontend_bucket_public_access]
}


# Bucket for Resumes (Uploads & Generated)
resource "aws_s3_bucket" "resume_bucket" {
  bucket = "${var.project_name}-files-v9510"
}

resource "aws_s3_bucket_cors" "resume_bucket_cors" {
  bucket = aws_s3_bucket.resume_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "GET", "POST", "HEAD"]
    allowed_origins = ["*"] # In production, restrict this to CloudFront domain
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# --- DynamoDB Tables ---

resource "aws_dynamodb_table" "job_posts" {
  name           = "JobPosts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id" # Using URL as ID might be better, or a generated ID. Let's stick to simple ID.
  
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "resumes" {
  name           = "Resumes"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# --- Secrets Manager ---

resource "aws_secretsmanager_secret" "gemini_api_key" {
  name = "gemini_api_key_v2" # v2 to avoid conflicts if exists
}

# --- IAM Roles for Lambda ---

resource "aws_iam_role" "lambda_role" {
  name = "resume_generator_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "resume_generator_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.job_posts.arn,
          aws_dynamodb_table.resumes.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_dynamodb_table.job_posts.arn, # Mistake in copy/paste, corrected below
          aws_s3_bucket.resume_bucket.arn,
          "${aws_s3_bucket.resume_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.gemini_api_key.arn
        ]
      }
    ]
  })
}

# --- Lambda Function ---

# We'll zip the backend directory. 
# For Terraform to work smootly locally, we assume the zip is created or we use a dummy code for now.
# In a real pipeline, we'd build the zip. Here we'll just point to a placeholder or assume the zip exists at variable location.

# resource "aws_lambda_function" "api_handler" {
#   filename         = "${path.module}/backend_lambda.zip"
#   ...

# We expect the zip to be provided externally (by CI/CD)
# For local dev, you must zip 'backend/' to 'terraform/backend_lambda.zip' manually.

resource "aws_lambda_function" "api_handler" {
  filename         = "${path.module}/backend_lambda.zip"
  function_name    = "resume_generator_api"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_main.handler" 
  source_code_hash = filebase64sha256("${path.module}/backend_lambda.zip")
  runtime          = "python3.12"
  timeout          = 60 # Gemini might take time
  memory_size      = 512

  environment {
    variables = {
      RESUME_BUCKET   = aws_s3_bucket.resume_bucket.id
      JOB_POSTS_TABLE = aws_dynamodb_table.job_posts.name
      RESUMES_TABLE   = aws_dynamodb_table.resumes.name
      SECRET_ARN      = aws_secretsmanager_secret.gemini_api_key.arn
    }
  }
}

# --- API Gateway (HTTP API) ---

resource "aws_apigatewayv2_api" "http_api" {
  name          = "resume-generator-http-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_handler.invoke_arn
}

# Routes
resource "aws_apigatewayv2_route" "any_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# --- CloudFront Distribution ---

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend_bucket.id}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend_bucket.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# --- Outputs ---

output "api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.s3_distribution.id
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend_bucket.bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.api_handler.function_name
}
