from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import google.generativeai as genai
import os


class GeminiRequester:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def request(self, text: str) -> str:
        response = self.model.generate_content(text)
        return response.text


# Usage example
if __name__ == "__main__":
    requester = GeminiRequester()
    response_text = requester.request("こんにちは。")
    print(response_text)
