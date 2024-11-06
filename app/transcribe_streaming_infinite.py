# `python /Users/takahashishohta/development/research-project/app/transcribe_streaming_infinite.py` で実行可能。

from __future__ import division
import re
import sys
import os
import pyaudio
import time
from google.cloud import speech
from six.moves import queue

# 環境変数でGoogle Cloud認証情報ファイルのパスを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/credentials.json"

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

LIMIT_TIME = 30  # 30秒間の音声を文字起こし

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
    """サーバーからの応答を受け取り、文字起こしを表示"""
    num_chars_printed = 0
    for response in responses:
        # 開始から30秒が経過したら終了
        if time.time() - start_time > LIMIT_TIME:
            print(LIMIT_TIME, "秒経過したので終了します。")
            break

        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break
            num_chars_printed = 0

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
