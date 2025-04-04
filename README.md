# 🌊 OES Buoy Ingest

A serverless cloud-based data ingestion and transformation system for simulated ocean buoy data. This project demonstrates a modern data pipeline using AWS Lambda, S3, Glue, and CI/CD via GitHub Actions.

---

## 📁 Project Structure

```bash
oes-buoy-ingest/
├── lambda/
│   ├── ingest/
│   │   └── lambda_function.py        # Generates simulated buoy data and stores it in S3 (raw/)
│   └── convert/
│       └── convert_function.py       # Converts raw JSON files to Parquet in S3 (processed/)
│
├── tests/
│   └── test_lambda.py                # Unit tests using unittest + moto
│
├── .github/
│   └── workflows/
│       └── deploy.yml                # CI/CD workflow
│
├── requirements.txt                 # Dependencies for production (Lambda)
├── requirements-dev.txt            # Dev-only dependencies (e.g., moto for testing)
├── README.md                        # This file
└── .gitignore                       # Ignore rules
```

---

## 🚀 Lambda Deployment via GitHub Actions

Every push to the `main` branch automatically triggers the CI/CD workflow:

1. Installs runtime and dependencies
2. Runs unit tests
3. Packages and deploys two AWS Lambda functions:
   - **`lambda_function.py`** → Ingests simulated sensor data
   - **`convert_function.py`** → Converts raw `.json` files to `.parquet`

---

### 🔐 GitHub Secrets Required

| Secret name               | Description                           |
|---------------------------|----------------------------------------|
| `AWS_ACCESS_KEY_ID`       | IAM access key                         |
| `AWS_SECRET_ACCESS_KEY`   | IAM secret key                         |
| `AWS_REGION`              | AWS region (e.g. `eu-west-3`)          |
| `LAMBDA_FUNCTION_NAME`    | Main ingestion Lambda function name    |

---

## 🧪 Running Tests Locally

Make sure you have `moto` and `boto3` installed:

```bash
pip install -r requirements-dev.txt
python -m unittest discover tests
```

The test suite includes:
- Validation of Lambda S3 uploads
- Data range assertions
- Bucket mocking via `moto`

---

## ☁️ AWS Services Used

- **AWS Lambda** – Serverless function hosting
- **Amazon S3** – Raw and processed data storage
- **AWS Glue** – Schema inference and Data Catalog
- **Amazon Athena** – SQL queries on S3 data
- **EventBridge Scheduler** – Automatic weekly execution
- **CloudWatch Logs** – Execution logging
- **IAM** – Fine-grained role and policy control

---

## 📈 Features

- 🔁 Weekly automation with EventBridge
- 📂 Folder-based S3 data lake (`raw/`, `processed/`)
- 🧹 Converts JSON → Parquet with Pandas + PyArrow
- ✅ Test-driven development
- 🧪 Isolated local testing with `moto`
- 💼 Production-ready GitHub Actions CI/CD

---

## 🧠 Planned Extensions

| Phase   | Feature                                  |
|---------|------------------------------------------|
| ✅ A     | Raw ingestion and transformation         |
| 🔄 B     | Machine Learning training in Colab       |
| 📊 C     | Visual dashboards with Looker or Power BI|
| 🛡️ D     | Access control, retention, monitoring    |

---

## 📸 Screenshots

Screenshots and evidence of the setup are hosted in a [private OneDrive folder] and used in the final academic report.

> *Note: Screenshots are not tracked by Git for space and relevance reasons.*

---

## 👤 Author

**BadTonyDeveloper**  
CLD7302 – Cloud Solutions  
Academic Year 2024/25  
The University of Boton

---

## 📄 License

This repository is for academic use only.  
All components are developed and deployed in a controlled educational environment.
