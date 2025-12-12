resource "aws_dynamodb_table" "resumes" {
  name           = "resumes-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-resumes"
    Environment = var.environment
  }
}
