import json
import boto3
import uuid
from datetime import datetime
import random
import os

# Create an S3 client for the specified AWS region
s3 = boto3.client('s3', region_name='eu-west-3')

# Get the bucket name from environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def generate_buoy_data():
    """
    Generates a simulated set of data representing ocean buoy sensor readings.
    Returns a dictionary with buoy ID, timestamp, location, and sensor data.
    """
    return {
        "buoy_id": f"buoy-{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "lat": round(random.uniform(48.0, 60.0), 5),   # Latitude in European range
            "lon": round(random.uniform(-10.0, 5.0), 5)    # Longitude in European range
        },
        "sea_temp_c": round(random.uniform(10.0, 18.0), 2),
        "wave_height_m": round(random.uniform(0.5, 3.0), 2),
        "current_speed_kph": round(random.uniform(1.0, 5.0), 2)
    }

def ingest_data_handler(event, context):
    """
    AWS Lambda entry point. Generates a buoy data record, 
    stores it in an S3 bucket, and returns a status response.
    """
    try:
        # Validate bucket name
        if not BUCKET_NAME:
            raise ValueError("BUCKET_NAME environment variable is not set.")

        # Generate simulated data
        data = generate_buoy_data()
        filename = f"raw/{data['buoy_id']}_{data['timestamp']}.json"

        # Upload JSON file to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=json.dumps(data),
            ContentType='application/json'
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data uploaded successfully',
                'file': filename
            })
        }

    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
