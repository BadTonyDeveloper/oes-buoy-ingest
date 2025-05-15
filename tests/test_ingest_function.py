import unittest
import boto3
import os
import json
from moto import mock_s3
import importlib
import sys

# Adjust path to ingest_handler
sys.path.append(os.path.join(os.path.dirname(__file__), "../lambda/ingest"))
import ingest_handler

class TestIngestLambdaFunction(unittest.TestCase):

    @mock_s3
    def test_ingest_generates_multiple_files(self):
        bucket_name = "test-bucket"
        os.environ["BUCKET_NAME"] = bucket_name
        importlib.reload(ingest_handler)

        s3 = boto3.client("s3", region_name="eu-west-3")
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"}
        )

        response = ingest_handler.ingest_data_handler({}, {})
        self.assertEqual(response["statusCode"], 200)

        body = json.loads(response["body"])
        files = body["files"]
        self.assertEqual(len(files), 20)

        objs = s3.list_objects_v2(Bucket=bucket_name, Prefix="raw/")
        self.assertEqual(objs["KeyCount"], 20)

if __name__ == '__main__':
    unittest.main()
