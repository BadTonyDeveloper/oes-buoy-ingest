"""Lambda function to merge all JSON batches in 'raw/' into ONE Parquet.

- Reads every *.json file under RAW_PREFIX.
- Concatenates all records into a single DataFrame.
- Writes **one** Parquet file to PROCESSED_PREFIX with a timestamp in the name.
"""
import boto3
import json
import pandas as pd
import io
import os
from datetime import datetime

s3 = boto3.client("s3", region_name="eu-west-3")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "oes-buoy-data-eu-west-3-dev")
RAW_PREFIX = "raw/"
PROCESSED_PREFIX = "processed/"

def lambda_handler(event=None, context=None):
    # 1. List JSON batch files
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=RAW_PREFIX)

    records = []
    raw_keys = []

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".json"):
                continue

            raw_keys.append(key)
            # 2. Download and load JSON
            res = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            payload = json.loads(res["Body"].read())

            # Ensure list of dicts
            if isinstance(payload, list):
                records.extend(payload)
            else:
                records.append(payload)

    if not records:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No JSON batch files to process."}),
        }

    # 3. Create DataFrame
    df = pd.json_normalize(records)

    # 4. Write ONE Parquet file
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    parquet_key = f"{PROCESSED_PREFIX}buoy_all_{timestamp}.parquet"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=parquet_key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream",
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Merged {len(raw_keys)} JSON files into one Parquet",
                "rows": len(df),
                "parquet_file": parquet_key,
            }
        ),
    }
