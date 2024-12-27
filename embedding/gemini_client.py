import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_code(self, prompt: str) -> str:
        """Geminiを使用してコードを生成します。

        Args:
            prompt: コード生成のためのプロンプト

        Returns:
            生成されたコード
        """
        try:
            response = self.model.generate_content(
                f"{prompt}。Pythonの関数コードのみを記述してください。他の説明や装飾は一切不要です。"
            )
            # 不要な部分（```python や ```）を取り除く
            code = response.text.strip()
            if code.startswith("```python"):
                code = code[len("```python") :].strip()
            if code.endswith("```"):
                code = code[: -len("```")].strip()
            return code
        except Exception as e:
            print(f"Error generating code with Gemini: {e}")
            return None
