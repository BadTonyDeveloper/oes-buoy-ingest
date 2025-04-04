import unittest
import json
import boto3
import os
import importlib
import pandas as pd
from io import BytesIO
from moto import mock_s3

# Import the function to test
import convert_function


class TestConvertLambdaFunction(unittest.TestCase):

    @mock_s3
    def test_json_to_parquet_conversion(self):
        """
        Test that the convert Lambda reads JSON from S3 and writes Parquet.
        """
        bucket_name = "oes-buoy-data-eu-west-3-dev"
        os.environ['BUCKET_NAME'] = bucket_name

        importlib.reload(convert_function)

        s3 = boto3.client('s3', region_name='eu-west-3')
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-3'}
        )

        # Create mock raw data file
        mock_json = {
            "buoy_id": "buoy-123abc",
            "timestamp": "2025-04-05T12:00:00Z",
            "location": {"lat": 52.52, "lon": 13.405},
            "sea_temp_c": 15.2,
            "wave_height_m": 1.1,
            "current_speed_kph": 2.9
        }

        raw_key = "raw/mock_data.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=raw_key,
            Body=json.dumps(mock_json),
            ContentType="application/json"
        )

        # Call the conversion lambda
        response = convert_function.lambda_handler({}, {})
        self.assertEqual(response['statusCode'], 200)

        # Check processed file exists
        processed_key = raw_key.replace("raw/", "processed/").replace(".json", ".parquet")
        result = s3.get_object(Bucket=bucket_name, Key=processed_key)
        parquet_content = result["Body"].read()

        # Validate Parquet file (loads to DataFrame)
        df = pd.read_parquet(BytesIO(parquet_content))
        self.assertEqual(df.shape[0], 1)
        self.assertIn("buoy_id", df.columns)
        self.assertEqual(df.iloc[0]["buoy_id"], "buoy-123abc")


if __name__ == '__main__':
    unittest.main()
