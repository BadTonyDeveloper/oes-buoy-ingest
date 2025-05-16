# OES Buoy Data Ingestion and Processing

This repository contains the implementation of a serverless, event-driven architecture for Oceanic Energy Solutions (OES) to simulate, ingest, transform, and (future) predict marine buoy sensor data. The solution leverages AWS services, GitHub Actions CI/CD, and Terraform IaC.

## This is test!
## 📁 Repository Structure
```
├── lambda
│   ├── ingest
│   │   └── ingest_handler.py          # Lambda function for data ingestion (Python 3.12)
│   └── convert
│       └── convert_function.py        # Container-based Lambda for JSON→Parquet conversion
├── requirements.txt                  # Production dependencies (boto3, pandas, pyarrow)
├── requirements-dev.txt              # Development dependencies (moto)
├── .github
│   └── workflows
│       ├── test.yml                  # CI workflow: unit tests
│       ├── deploy-lambda.yml         # CD workflow: ZIP-based Lambda deploy
│       └── deploy-container.yml      # CD workflow: ECR container deploy
└── terraform
    └── monitoring
        ├── main.tf                   # Terraform resources: SNS topic & CloudWatch alarms
        └── variables.tf              # Input variables for Terraform
``` 

## 🚀 Getting Started

### Prerequisites
- Python 3.12
- Docker (for container-based Lambda)
- AWS CLI configured with a user having appropriate IAM permissions
- Terraform (>=1.3.0)

### Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/oes-buoy-ingest.git
   cd oes-buoy-ingest
   ```

2. **Install production dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies** (for local testing):
   ```bash
   pip install -r requirements-dev.txt
   ```

## 🧪 Running Tests

Execute all unit tests in the `tests/` directory using pytest or unittest:
```bash
python -m unittest discover tests
``` 

## ⚙️ CI/CD Workflows

Three GitHub Actions workflows automate testing and deployment:
- **`test.yml`**: Runs unit tests on every push and pull request.
- **`deploy-lambda.yml`**: Packages Lambda functions into ZIPs, uploads to S3 (`oes-lambda-deploy-eu-west-3`), and updates functions.
- **`deploy-container.yml`**: Builds and pushes Docker image to ECR, then updates container-based Lambda.

## ☁️ AWS Services Overview

| Component            | Service               | Purpose                                                                 |
|----------------------|-----------------------|-------------------------------------------------------------------------|
| Ingestion Lambda     | AWS Lambda            | Generate simulated buoy data and store JSON in S3 `raw/`                |
| Conversion Lambda    | AWS Lambda (Container)| Convert JSON to Parquet and store in S3 `processed/`                    |
| Scheduler            | Amazon EventBridge    | Weekly triggers for ingestion and conversion                           |
| Storage              | Amazon S3             | Buckets for raw JSON and processed Parquet                              |
| Container Registry   | Amazon ECR            | Stores Docker image for conversion Lambda                               |
| Monitoring & Alerts  | CloudWatch & SNS      | Logs, metrics, alarms; notification via email                           |
| IaC                  | Terraform             | Defines SNS topic and CloudWatch alarms                                 |
| CI/CD                | GitHub Actions        | Automates tests and deployments                                         |

## 📦 Packaging & Deployment

### ZIP-based Lambda
```bash
# Package ingestion Lambda
cd lambda/ingest
zip -r ../../../ingest_handler.zip .
# Package conversion Lambda
cd ../convert
zip -r ../../../convert_function.zip .
# Upload to S3
aws s3 cp ingest_handler.zip s3://oes-lambda-deploy-eu-west-3/ingest_handler.zip
aws s3 cp convert_function.zip s3://oes-lambda-deploy-eu-west-3/convert_function.zip
# Deploy
aws lambda update-function-code --function-name $INGEST_LAMBDA_NAME --s3-bucket oes-lambda-deploy-eu-west-3 --s3-key ingest_handler.zip
aws lambda update-function-code --function-name $CONVERT_LAMBDA_NAME --s3-bucket oes-lambda-deploy-eu-west-3 --s3-key convert_function.zip
```

### Container-based Lambda
```bash
# Build and tag image
docker build -t lambda-convert-container ./lambda/convert
docker tag lambda-convert-container:latest 123456789012.dkr.ecr.eu-west-3.amazonaws.com/lambda-convert-container:latest
# Push to ECR
docker push 123456789012.dkr.ecr.eu-west-3.amazonaws.com/lambda-convert-container:latest
# Update Lambda
aws lambda update-function-code --function-name $CONVERT_LAMBDA_NAME --image-uri 123456789012.dkr.ecr.eu-west-3.amazonaws.com/lambda-convert-container:latest
```

## 🌐 Terraform Monitoring

Initialize and apply Terraform in `terraform/monitoring`:
```bash
cd terraform/monitoring
terraform init
terraform apply
```

## 📝 License
MIT License. See [LICENSE](LICENSE).

---

*Prepared for CLD7302: Cloud Solutions and Implementation.*
