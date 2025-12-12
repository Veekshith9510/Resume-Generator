# AI Resume Generator (Serverless AWS)

This project is a cloud-native, serverless Resume Generator application. It allows users to upload a resume, scrape a job description from a URL, and use Google Gemini AI to generate a tailored resume.

## Architecture

Migation to AWS Serverless Architecture:

```mermaid
graph TD
    User[User] -->|HTTPS| CF[CloudFront]
    CF -->|Serves UI| S3Front[S3 Bucket: Frontend]
    User -->|API Calls| APIGW[API Gateway]
    APIGW -->|Proxy| Lambda[AWS Lambda (Python)]
    Lambda -->|Read/Write| DB[DynamoDB]
    Lambda -->|Read Uploads| S3Uploads[S3 Bucket: Uploads]
    Lambda -->|Write Resumes| S3Gen[S3 Bucket: Generated]
    Lambda -->|Get Key| Secrets[Secrets Manager]
    Lambda -->|Generate| Gemini[Gemini AI]
```

### ASCII Diagram

```
       +--------+
       |  User  |
       +---+----+
           |
    +------+-------+
    |              |
+---v----+     +---v---------+
| Cloud- |     | API Gateway |
| Front  |     +------+------+
+---+----+            |
    |          +------v------+      +-----------+
+---v----+     | AWS Lambda  +------> Gemini AI |
| S3 UI  |     +---+---+-----+      +-----------+
+--------+         |   |
             +-----v---v-----+
             |   DynamoDB    |
             |   + S3 Files  |
             +---------------+
```

## Tech Stack

- **Frontend**: React (Vite)
- **Backend**: AWS Lambda (Python 3.12, FastAPI, Mangum)
- **Database**: Amazon DynamoDB
- **Storage**: Amazon S3
- **AI**: Google Gemini Flash (via Generative AI SDK)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

## Deployment

### Prerequisites

1. AWS Account
2. GitHub Repository
3. Gemini API Key

### Steps

1. **Configure Secrets**: Add the following secrets to your GitHub Repository:
   - `AWS_ACCESS_KEY_ID`: Your AWS Access Key.
   - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Key.
   - `GEMINI_API_KEY`: Your Google Gemini API Key.

2. **Deploy**: Push to the `main` branch. The GitHub Actions workflow will:
   - Build the backend Lambda package.
   - Provision infrastructure using Terraform.
   - Build and deploy the Frontend to S3.
   - Update the Gemini API Key in Secrets Manager.

3. **Access**:
   - The workflow output (and Terraform output) will provide the `cloudfront_domain`. Access this URL to use the application.

## Local Development (Optional)

You can run the application locally using the `dev` scripts, but you must configure `.env` to point to local backend or deployed API.

- Backend: `cd backend && uvicorn lambda_main:app --reload`
- Frontend: `cd frontend && npm run dev`

## File Structure

- `/backend`: Python backend code (Lambda-ready).
- `/frontend`: React frontend code.
- `/terraform`: Infrastructure as Code configuration.
- `/.github/workflows`: CI/CD pipelines.
