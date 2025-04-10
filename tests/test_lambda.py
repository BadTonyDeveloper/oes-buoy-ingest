import unittest
from unittest.mock import patch
from moto import mock_s3
import boto3
import os
import json
import importlib
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../lambda/ingest"))
import ingest_handler as lambda_function


class TestLambdaFunction(unittest.TestCase):

    @mock_s3
    def test_lambda_handler_success(self):
        bucket_name = "oes-buoy-data-eu-west-3-dev"
        os.environ['BUCKET_NAME'] = bucket_name
        importlib.reload(lambda_function)

        s3 = boto3.client('s3', region_name='eu-west-3')
        s3.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': 'eu-west-3'})

        response = lambda_function.lambda_handler({}, {})
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

        self.assertGreaterEqual(content['sea_temp_c'], 10.0)
        self.assertLessEqual(content['sea_temp_c'], 18.0)
        self.assertGreaterEqual(content['wave_height_m'], 0.5)
        self.assertLessEqual(content['wave_height_m'], 3.0)
        self.assertGreaterEqual(content['current_speed_kph'], 1.0)
        self.assertLessEqual(content['current_speed_kph'], 5.0)

    @mock_s3
    def test_lambda_handler_missing_bucket_env(self):
        if 'BUCKET_NAME' in os.environ:
            del os.environ['BUCKET_NAME']
        importlib.reload(lambda_function)
        response = lambda_function.lambda_handler({}, {})
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)


if __name__ == '__main__':
    unittest.main()
