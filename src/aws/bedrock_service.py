import json
import boto3


class BedrockService:

    def __init__(
        self,
        region_name="ap-south-1",
        model_id=None
    ):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name
        )

        self.model_id = model_id

    def extract_entities(self, text):

        prompt = f"""
Extract entities and relationships from the following library document.

Return JSON with this structure:

{{
    "entities": [],
    "relationships": []
}}

Document:

{text}
"""

        body = {
            "prompt": prompt
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = response["body"].read().decode("utf-8")

        return result