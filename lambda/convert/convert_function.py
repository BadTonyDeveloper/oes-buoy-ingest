import boto3
import json
import pandas as pd
import io
import os

s3 = boto3.client('s3', region_name='eu-west-3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'oes-buoy-data-eu-west-3-dev')
RAW_PREFIX = 'raw/'
PROCESSED_PREFIX = 'processed/'

def lambda_handler(event=None, context=None):
    """
    Reads JSON batch(s) from S3 RAW_PREFIX, converts them to Parquet,
    and writes to S3 PROCESSED_PREFIX.
    """
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=RAW_PREFIX)
    objects = response.get('Contents', [])

    for obj in objects:
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        res = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        raw = json.loads(res['Body'].read())

        records = raw if isinstance(raw, list) else [raw]
        df = pd.json_normalize(records)

        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)

        new_key = key.replace(RAW_PREFIX, PROCESSED_PREFIX).replace('.json', '.parquet')

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=new_key,
            Body=buffer.getvalue(),
            ContentType='application/octet-stream'
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Conversion completed', 'processed_count': len(objects)})
    }
