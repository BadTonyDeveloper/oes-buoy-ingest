import json
import boto3
import uuid
import os
import random
from datetime import datetime

# S3 client
s3 = boto3.client("s3", region_name="eu-west-3")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")

def generate_buoy_data() -> dict:
    """Return one simulated buoy reading."""
    return {
        "buoy_id": f"buoy-{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "lat": round(random.uniform(48.0, 60.0), 5),
            "lon": round(random.uniform(-10.0, 5.0), 5),
        },
        "sea_temp_c": round(random.uniform(10.0, 18.0), 2),
        "wave_height_m": round(random.uniform(0.5, 3.0), 2),
        "current_speed_kph": round(random.uniform(1.0, 5.0), 2),
    }

def ingest_data_handler(event, context):
    """Generate *num_readings* buoy readings and upload **one** JSON file to S3.

    env:
        BUCKET_NAME must be set.

    event:
        { "num_readings": 20 }  # optional, defaults to 20
    """
    if not BUCKET_NAME:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "BUCKET_NAME environment variable not set"}),
        }

    # Get desired number of readings
    try:
        num_readings = int(event.get("num_readings", 20)) if isinstance(event, dict) else 20
    except (ValueError, TypeError):
        num_readings = 20

    readings = [generate_buoy_data() for _ in range(num_readings)]

    filename = (
        "raw/"
        f"buoy_batch_{datetime.utcnow():%Y%m%dT%H%M%SZ}_"
        f"{uuid.uuid4().hex[:4]}.json"
    )

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=json.dumps(readings),
            ContentType="application/json",
        )
    except Exception as exc:
        return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f"{num_readings} readings uploaded", "file": filename}
        ),
    }
