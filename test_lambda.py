import unittest
from unittest.mock import patch
from moto import mock_s3
import boto3
import os
import json

# Import the Lambda function to test
import lambda_function


class TestLambdaFunction(unittest.TestCase):

    @mock_s3
    def test_lambda_handler_success(self):
        """
        Test that the Lambda function successfully uploads data to S3
        and returns the correct response structure and valid sensor data.
        """
        bucket_name = "oes-buoy-data-eu-west-3-dev"
        os.environ['BUCKET_NAME'] = bucket_name

        # Mock an S3 bucket in the correct region
        s3 = boto3.client('s3', region_name='eu-west-3')
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-3'}
        )

        # Call the Lambda function
        response = lambda_function.lambda_handler({}, {})
        self.assertEqual(response['statusCode'], 200)

        # Parse and check response content
        body = json.loads(response['body'])
        self.assertIn('message', body)
        self.assertIn('file', body)
        self.assertTrue(body['file'].startswith('raw/'))

        # Retrieve and verify uploaded object
        result = s3.get_object(Bucket=bucket_name, Key=body['file'])
        content = json.loads(result['Body'].read())

        # Check expected keys and value ranges
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
        """
        Test that the Lambda function returns an error 
        when the BUCKET_NAME environment variable is not set.
        """
        if 'BUCKET_NAME' in os.environ:
            del os.environ['BUCKET_NAME']

        response = lambda_function.lambda_handler({}, {})
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)


if __name__ == '__main__':
    unittest.main()
