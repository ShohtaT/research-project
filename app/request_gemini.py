# INFO: `python3 ./app/request_gemini.py` で実行可能。

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import csv
import os
import google.generativeai as genai


class GeminiRequester:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def request(self, text: str) -> str:
        response = self.model.generate_content(text)
        return response.text


def main(csv: str):
    """指定されたCSVファイルを解析し、Geminiにプロンプトを送信して応答を取得します。"""
    # CSVファイルの解析
    try:
        parsed_data = parse_csv(csv_path=csv)
        print("文字起こししたデータ ================ \n", parsed_data, "\n===========================================")
    except FileNotFoundError:
        print(f"CSVファイルが見つかりません: {csv}")
        return
    except Exception as e:
        print(f"CSV解析中にエラーが発生しました: {e}")
        return

    # プロンプト生成
    prompt_text = generate_prompt(parsed_data)

    # Geminiへリクエスト
    print("Requesting Gemini...")
    requester = GeminiRequester()
    try:
        response = requester.request(prompt_text)
        print("Geminiの応答 ================ \n", response, "\n===========================================")
    except Exception as e:
        print(f"Geminiリクエスト中にエラーが発生しました: {e}")


def parse_csv(csv_path: str) -> str:
    """CSVファイルを解析して、すべての行のデータを1つの文字列として結合して返します。"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = [list(row.values())[0] for row in reader] # すべての行のデータを1列目から取得して結合

    result = " ".join(data)
    return result


def generate_prompt(data: str) -> str:
    """CSVデータを基にGeminiに送信するプロンプトを生成します。"""
    if not data:
        return "データが空です。"

    # TODO: プロンプトを考える
    prompt = f"以下のデータを要約してください:\n {data}\n"

    return prompt
