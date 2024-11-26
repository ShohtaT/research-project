# INFO: 本番では使わないが、マスタデータ作成時に音声データを文字起こしするためのスクリプト。
# INFO: `python3 ./app/transcribe_streaming_for_master_data.py` で実行可能。

from __future__ import division
import os
from datetime import datetime
import time
import csv
import pyaudio
from google.cloud import speech
from six.moves import queue

# 環境変数でGoogle Cloud認証情報ファイルのパスを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/credentials.json"

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# FIXME: 以下の変数を適切な値に変更してください
WRITE_INTERVAL = 10  # 10秒ごとに書き込み


class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        """ストリームを開いて音声データの取得を開始"""
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        """ストリームを停止・終了"""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """非同期でデータを取得し、バッファに保存"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """バッファから音声データを連続して提供するジェネレータ"""
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)


def display_transcriptions(responses, start_time):
    """サーバーからの応答を受け取り、文字起こしを表示し、確定した文字起こしをCSVに保存"""
    last_write_time = start_time  # 最後にCSVに書き込んだ時間
    last_written_transcript = ""  # 最後にCSVに書き込んだ文字

    # 現在の日時を取得し、ファイル名に反映
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_results/{timestamp}.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            # sys.stdout.write(transcript + "\r")
            # sys.stdout.flush()

            # 差分を取得
            diff = transcript[len(last_written_transcript):]

            # WRITE_INTERVAL 秒ごとにCSVに書き込み
            if time.time() - last_write_time >= WRITE_INTERVAL:
                writer.writerow([diff])
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ": ", diff)
                last_written_transcript = transcript  # 最後の書き込み内容を更新
                last_write_time = time.time()  # 最後の書き込み時間を更新


def main():
    """音声ストリーミングを設定して実行するメイン関数"""
    language_code = "ja-JP"
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    start_time = time.time()  # 開始時刻を記録

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)
        responses = client.streaming_recognize(streaming_config, requests)
        display_transcriptions(responses, start_time)  # 開始時刻を渡す


if __name__ == "__main__":
    main()
