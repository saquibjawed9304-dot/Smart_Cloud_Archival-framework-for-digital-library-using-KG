import boto3


class TextractService:

    def __init__(self, region_name="ap-south-1"):
        self.client = boto3.client(
            "textract",
            region_name=region_name
        )

    def analyze_document(self, bucket, key):

        response = self.client.detect_document_text(
            Document={
                "S3Object": {
                    "Bucket": bucket,
                    "Name": key
                }
            }
        )

        lines = []

        for block in response.get("Blocks", []):
            if block["BlockType"] == "LINE":
                lines.append(block.get("Text", ""))

        return "\n".join(lines)