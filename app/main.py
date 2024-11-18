# INFO: `python3 ./app/main.py` で実行可能。

import glob
import os
import transcribe_streaming_infinite as transcribe
import request_gemini as gemini


def main():
    print("Start main function.")
    # 3分間文字起こしを行い、csv を作成する。
    transcribe.main()

    # transcription_resultsディレクトリ内の最新のCSVをファイル名順で取得する
    try:
        latest_csv = get_latest_csv()
        print(f"CSV: {latest_csv}")
    except FileNotFoundError as e:
        print(e)
        return

    # csv で Gemini にリクエストする
    res = gemini.main(csv=latest_csv)
    print(res)


def get_latest_csv():
    """指定したディレクトリ内の最新のCSVファイルを取得する"""
    files = glob.glob(f"transcription_results/*.csv")
    if not files:
        raise FileNotFoundError("CSVファイルが見つかりません。")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

if __name__ == "__main__":
    main()
