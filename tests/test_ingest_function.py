import unittest
from unittest.mock import patch
from moto import mock_s3
import boto3
import os
import json
import importlib
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../lambda/ingest"))
import ingest_handler


class TestIngestLambdaFunction(unittest.TestCase):

    @mock_s3
    def test_ingest_data_handler_success(self):
        bucket_name = "oes-buoy-data-eu-west-3-dev"
        os.environ['BUCKET_NAME'] = bucket_name
        importlib.reload(ingest_handler)

        s3 = boto3.client('s3', region_name='eu-west-3')
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-3'}
        )

        response = ingest_handler.ingest_data_handler({}, {})
        self.assertEqual(response['statusCode'], 200)

        body = json.loads(response['body'])
        self.assertIn('message', body)
        self.assertIn('file', body)
        self.assertTrue(body['file'].startswith('raw/'))

        result = s3.get_object(Bucket=bucket_name, Key=body['file'])
        content = json.loads(result['Body'].read())

        self.assertIn('buoy_id', content)
        self.assertIn('timestamp', content)
        self.assertIn('location', content)
        self.assertIn('sea_temp_c', content)
        self.assertIn('wave_height_m', content)
        self.assertIn('current_speed_kph', content)

    @mock_s3
    def test_ingest_data_handler_missing_bucket_env(self):
        if 'BUCKET_NAME' in os.environ:
            del os.environ['BUCKET_NAME']
        importlib.reload(ingest_handler)
        response = ingest_handler.ingest_data_handler({}, {})
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)


if __name__ == '__main__':
    unittest.main()