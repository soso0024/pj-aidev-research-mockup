import boto3
import json


class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name="ap-northeast-1"  # Tokyo region
        )

    def get_embedding(self, text: str):
        """テキストの埋め込みベクトルを取得します。"""
        model_id = "amazon.titan-embed-text-v1"
        body = json.dumps({"inputText": text})
        accept = "application/json"
        content_type = "application/json"

        response = self.client.invoke_model(
            body=body, modelId=model_id, accept=accept, contentType=content_type
        )
        response_body = json.loads(response.get("body").read())
        embedding = response_body.get("embedding")
        return embedding