import boto3


class TextractService:

    def __init__(self, region_name="ap-south-1"):
        self.client = boto3.client(
            "textract",
            region_name=region_name
        )

    def start_text_detection(self, bucket, key):
        response = self.client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        return response["JobId"]

    def get_text_detection(self, job_id):
        response = self.client.get_document_text_detection(JobId=job_id)
        lines = [
            block.get("Text", "")
            for block in response.get("Blocks", [])
            if block.get("BlockType") == "LINE"
        ]
        return {
            "status": response.get("JobStatus", "UNKNOWN"),
            "text": "\n".join(lines),
            "next_token": response.get("NextToken"),
        }

    def analyze_document(self, bucket, key):
        job_id = self.start_text_detection(bucket, key)
        return {"job_id": job_id, "status": "IN_PROGRESS"}

    def collect_text(self, job_id):
        result = self.get_text_detection(job_id)
        lines = [result["text"]]
        while result.get("next_token"):
            response = self.client.get_document_text_detection(
                JobId=job_id,
                NextToken=result["next_token"],
            )
            lines.extend(
                block.get("Text", "")
                for block in response.get("Blocks", [])
                if block.get("BlockType") == "LINE"
            )
            result = {"next_token": response.get("NextToken")}
        return "\n".join(line for line in lines if line)