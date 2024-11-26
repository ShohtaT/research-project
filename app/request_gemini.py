# INFO: `python3 ./app/request_gemini.py` で実行可能。

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import csv
import os
import pandas as pd
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
    # 1. CSVファイルの解析
    try:
        parsed_data = parse_csv(csv_path=csv)
        print("文字起こししたデータ ================ \n", parsed_data, "\n===========================================")
    except FileNotFoundError:
        print(f"CSVファイルが見つかりません: {csv}")
        return
    except Exception as e:
        print(f"CSV解析中にエラーが発生しました: {e}")
        return

    # 2. ドラマデータセットの読み込みと、プロンプト生成
    prompt_text = generate_prompt(parsed_data)

    # 3. Geminiへリクエスト
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
        data = [list(row.values())[0] for row in reader]  # すべての行のデータを1列目から取得して結合

    result = " ".join(data)
    return result


def generate_prompt(data: str) -> str:
    """CSVデータを基にGeminiに送信するプロンプトを生成します。"""
    if not data:
        return "データが空です。"

    # データセットの読み込み、文字列として保持する
    df = pd.read_csv(f"drama_dataset/data.csv")
    dataset = df.to_csv(index=False)

    # TODO: プロンプトを考える
    prompt = (
        "これは「BGM名」と「会話テキスト」のアノテーションデータ（A）です。"
        "これにより、どんな会話にどんなBGMが使用されているのかという特徴が見えてくるはずです。"
        f"\n {dataset}\n"
        "これを用いて、以下のことを行なってください。"
        f"以下のデータは、実際に行われた会話です。これに類似する会話テキストを探索し、Aに対応するBGM名を上位3つ提示してください。"
        f"\n {data}\n")

    print("プロンプト ================ \n", prompt, "\n===========================================")

    return prompt
