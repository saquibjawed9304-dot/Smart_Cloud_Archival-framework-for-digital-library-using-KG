import boto3
from pathlib import Path
from uuid import uuid4


class S3Service:

    def __init__(self, bucket_name, region_name="ap-south-1"):
        self.bucket_name = bucket_name

        self.client = boto3.client(
            "s3",
            region_name=region_name
        )

    def upload_file(self, file_path, object_name=None, content_type="application/pdf"):

        if object_name is None:
            object_name = f"documents/{uuid4().hex}_{Path(file_path).name}"

        self.client.upload_file(
            file_path,
            self.bucket_name,
            object_name,
            ExtraArgs={
                "ContentType": content_type,
                "ServerSideEncryption": "AES256",
            },
        )

        return {
            "bucket": self.bucket_name,
            "object": object_name
        }