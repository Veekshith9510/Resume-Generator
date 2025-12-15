# Deployment Setup Guide

## GitHub Actions Workflow

The `.github/workflows/deploy.yml` file has been configured to automate the deployment of both backend and frontend components to AWS.

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

### AWS Credentials
- **`AWS_ACCESS_KEY_ID`**: Your AWS access key ID
- **`AWS_SECRET_ACCESS_KEY`**: Your AWS secret access key
- **`AWS_REGION`**: AWS region where resources will be deployed (e.g., `us-east-1`)

### API Keys
- **`GEMINI_API_KEY`**: Your Google Gemini API key (will be automatically uploaded to AWS Secrets Manager)

## Workflow Overview

### Backend Pipeline

1. **Setup Python 3.12**: Installs Python runtime
2. **Package Lambda**: Creates a deployment package with dependencies
3. **Upload to AWS Lambda**: Packages backend code into ZIP format
4. **Terraform Workflow**:
   - `terraform fmt -check`: Validates code formatting
   - `terraform validate`: Validates configuration syntax
   - `terraform plan`: Creates execution plan
   - `terraform apply`: Deploys infrastructure

### Frontend Pipeline (React + Vite)

1. **Install Dependencies**: Runs `npm install`
2. **Build Application**: Runs `npm run build` with API endpoint from Terraform outputs
3. **Deploy to S3**: Syncs build output to S3 bucket
4. **CloudFront Invalidation**: Clears CDN cache for immediate updates

## Key Features

✅ **Automatic Secret Management**: GEMINI_API_KEY is automatically uploaded to AWS Secrets Manager  
✅ **Infrastructure as Code**: Full Terraform validation before deployment  
✅ **Zero-Downtime Deploys**: S3 sync with CloudFront cache invalidation  
✅ **Branch Protection**: Only deploys on `main` branch pushes  
✅ **Manual Trigger**: Can be triggered manually via GitHub Actions UI

## Terraform Outputs

The workflow expects the following Terraform outputs:
- `api_endpoint`: API Gateway endpoint URL
- `frontend_bucket`: S3 bucket name for frontend
- `cloudfront_domain`: CloudFront distribution domain
- `cloudfront_distribution_id`: CloudFront distribution ID for cache invalidation

## Deployment Trigger

The workflow runs automatically:
- On every push to the `main` branch
- Manually via the GitHub Actions UI (`Actions` tab → `Deploy to AWS` → `Run workflow`)

## First-Time Setup

1. Add all required secrets to GitHub repository
2. Ensure Terraform backend is configured (S3 + DynamoDB for state locking)
3. Push to `main` branch or manually trigger the workflow
4. Monitor the GitHub Actions tab for deployment progress

## Troubleshooting

### Terraform Format Check Fails
Run `terraform fmt` locally in the `terraform/` directory before committing.

### CloudFront Invalidation Fails
Ensure the Terraform output `cloudfront_distribution_id` is properly defined.

### Secrets Manager Update Fails
Verify that the secret `gemini_api_key_v2` exists in AWS Secrets Manager or update the secret ID in the workflow.
