import boto3


class S3Service:

    def __init__(self, bucket_name, region_name="ap-south-1"):
        self.bucket_name = bucket_name

        self.client = boto3.client(
            "s3",
            region_name=region_name
        )

    def upload_file(self, file_path, object_name=None):

        if object_name is None:
            object_name = file_path.split("/")[-1]

        self.client.upload_file(
            file_path,
            self.bucket_name,
            object_name
        )

        return {
            "bucket": self.bucket_name,
            "object": object_name
        }