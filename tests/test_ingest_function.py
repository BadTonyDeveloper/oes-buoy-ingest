import unittest
import boto3
import os
import json
from moto import mock_s3
import importlib
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../lambda/ingest"))
import ingest_handler

class TestIngestLambdaFunction(unittest.TestCase):
    @mock_s3
    def test_ingest_generates_single_batch_file(self):
        bucket_name = "test-bucket"
        os.environ["BUCKET_NAME"] = bucket_name
        importlib.reload(ingest_handler)

        s3 = boto3.client("s3", region_name="eu-west-3")
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
        )

        response = ingest_handler.ingest_data_handler({"num_readings": 10}, {})
        self.assertEqual(response["statusCode"], 200)

        body = json.loads(response["body"])
        batch_file = body["file"]
        self.assertTrue(batch_file.startswith("raw/"))

        # Ensure exactly one object
        objs = s3.list_objects_v2(Bucket=bucket_name, Prefix="raw/")
        self.assertEqual(objs["KeyCount"], 1)

        # Validate JSON content length == 10
        obj = s3.get_object(Bucket=bucket_name, Key=batch_file)
        content = json.loads(obj["Body"].read())
        self.assertEqual(len(content), 10)

if __name__ == "__main__":
    unittest.main()
