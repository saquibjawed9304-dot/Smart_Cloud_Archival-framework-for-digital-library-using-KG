import json
import boto3
import re


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

        if not self.model_id:
            raise ValueError("BEDROCK_MODEL_ID must be configured")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        payload = json.loads(response["body"].read().decode("utf-8"))
        text = "".join(item.get("text", "") for item in payload.get("content", []))
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Bedrock returned no JSON entity payload")
        result = json.loads(match.group(0))
        if not isinstance(result.get("entities"), list) or not isinstance(result.get("relationships"), list):
            raise ValueError("Bedrock entity payload has an invalid shape")
        return result