import boto3
import json
import pandas as pd
import io
import os

s3 = boto3.client("s3", region_name="eu-west-3")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "oes-buoy-data-eu-west-3-dev")
RAW_PREFIX = "raw/"
PROCESSED_PREFIX = "processed/"

def lambda_handler(event=None, context=None):
    """Convert any JSON batch files in RAW_PREFIX to Parquet in PROCESSED_PREFIX."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=RAW_PREFIX)
    objects = response.get("Contents", [])

    processed = 0

    for obj in objects:
        key = obj["Key"]
        if not key.endswith(".json"):
            continue

        res = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        payload = json.loads(res["Body"].read())

        records = payload if isinstance(payload, list) else [payload]
        df = pd.json_normalize(records)

        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")

        new_key = key.replace(RAW_PREFIX, PROCESSED_PREFIX).replace(".json", ".parquet")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=new_key,
            Body=buffer.getvalue(),
            ContentType="application/octet-stream",
        )
        processed += 1

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Conversion completed", "processed_files": processed}),
    }
