import boto3
import json
import torch
from transformers import AutoTokenizer, AutoModel


class BedrockClient:
    def __init__(self):
        # """
        # Bedrock client initialization (commented out but preserved)
        self.client = boto3.client(
            service_name="bedrock-runtime", region_name="ap-northeast-1"  # Tokyo region
        )
        # """

        # Initialize CodeBERT model and tokenizer
        # self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        # self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        # self.model.eval()  # Set model to evaluation mode

    def get_embedding(self, text: str):
        """テキストの埋め込みベクトルを取得します。"""
        # Original Bedrock implementation (commented out but preserved)

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

        # # CodeBERT implementation
        # # Tokenize the input text
        # inputs = self.tokenizer(
        #     text, return_tensors="pt", padding=True, truncation=True, max_length=512
        # )

        # # Get embeddings
        # with torch.no_grad():  # Disable gradient calculation for inference
        #     outputs = self.model(**inputs)

        # # Use the [CLS] token embedding as the code representation
        # # Shape: [1, 768] -> convert to list
        # embedding = outputs.last_hidden_state[0, 0, :].numpy().tolist()

        # return embedding
