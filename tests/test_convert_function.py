import unittest
import json
import boto3
import os
import importlib
import pandas as pd
from io import BytesIO
from moto import mock_s3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../lambda/convert"))
import convert_function

class TestConvertLambdaFunction(unittest.TestCase):
    @mock_s3
    def test_json_batch_to_parquet(self):
        bucket_name = "oes-buoy-data-eu-west-3-dev"
        os.environ["BUCKET_NAME"] = bucket_name
        importlib.reload(convert_function)

        s3 = boto3.client("s3", region_name="eu-west-3")
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
        )

        # Subimos un batch JSON simulado
        batch = []
        for i in range(5):
            batch.append(
                {
                    "buoy_id": f"buoy-{i}",
                    "timestamp": "2025-04-05T12:00:00Z",
                    "location": {"lat": 52.52 + i, "lon": 13.405},
                    "sea_temp_c": 14.0 + i,
                    "wave_height_m": 1.0 + 0.1 * i,
                    "current_speed_kph": 2.5 + 0.2 * i,
                }
            )

        raw_key = "raw/buoy_batch_test.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=raw_key,
            Body=json.dumps(batch),
            ContentType="application/json",
        )

        # Ejecutamos Lambda y obtenemos la respuesta
        response = convert_function.lambda_handler({}, {})
        self.assertEqual(response["statusCode"], 200)

        body = json.loads(response["body"])
        parquet_key = body["parquet_file"]
        self.assertTrue(parquet_key.startswith("processed/buoy_all_"))

        # Comprobamos el contenido del Parquet
        result = s3.get_object(Bucket=bucket_name, Key=parquet_key)
        parquet_content = result["Body"].read()

        df = pd.read_parquet(BytesIO(parquet_content))
        self.assertEqual(df.shape[0], 5)
        self.assertIn("buoy_id", df.columns)
        self.assertEqual(set(df["buoy_id"]), {f"buoy-{i}" for i in range(5)})

if __name__ == "__main__":
    unittest.main()
