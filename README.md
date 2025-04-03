# OES Buoy Ingest (Lambda · Python 3.12)

This project contains an AWS Lambda function (written in Python 3.12) to simulate and ingest oceanic buoy data into Amazon S3, as part of the Oceanic Energy Solutions (OES) cloud solution prototype.

## 🧩 Project Components

- **lambda_function.py**: Main function that generates and uploads JSON data to S3.
- **test_lambda.py**: Unit tests using `unittest` and `moto` to mock AWS services.
- **requirements.txt**: Dependencies to install locally.

## 📦 How to deploy

1. Zip the function:
    ```bash
    zip function.zip lambda_function.py
    ```

2. Upload to AWS Lambda via console or CLI.

## ✅ Environment Variables

- `oes-buoy-data-eu-west-3-dev`: S3 bucket to store data

## 🧪 Run tests

```bash
pip install -r requirements.txt
python -m unittest test_lambda.py
