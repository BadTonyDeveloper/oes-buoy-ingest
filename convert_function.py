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
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=RAW_PREFIX)
    objects = response.get('Contents', [])

    for obj in objects:
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        res = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        json_data = json.loads(res['Body'].read())

        df = pd.json_normalize(json_data)

        out_buffer = io.BytesIO()
        df.to_parquet(out_buffer, index=False)

        new_key = key.replace(RAW_PREFIX, PROCESSED_PREFIX).replace('.json', '.parquet')

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=new_key,
            Body=out_buffer.getvalue(),
            ContentType='application/octet-stream'
        )

    return {'message': f'{len(objects)} files processed.'}
