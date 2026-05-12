import requests
import subprocess
import tempfile
import os

SPEAKER_ID = 8
SPEED_SCALE = 1.0 # 読み上げ速度 (1.0が標準、1.3〜1.5が聞き取りやすく速い)

def make(text: str):
    base_url = "http://localhost:50021"

    # 読みと分かち書きを自動生成
    reading_text = text
    print(f"[tts] 読み上げ用テキスト: {reading_text[:50]}...")

    try:
        # 1. Generate audio query
        query_res = requests.post(
            f"{base_url}/audio_query",
            params={"text": reading_text, "speaker": SPEAKER_ID},
            timeout=5
        )
        query_res.raise_for_status()
        query_data = query_res.json()

        # 読み上げ速度（話速）を調整
        query_data["speedScale"] = SPEED_SCALE

        # 2. Synthesize audio
        synthesis_res = requests.post(
            f"{base_url}/synthesis",
            params={"speaker": SPEAKER_ID},
            json=query_data,
            timeout=30
        )
        synthesis_res.raise_for_status()

        # 3. Write to temporary file and play
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(synthesis_res.content)
            return tmp_path
    except Exception as e:
        print(f"[tts] VOICEVOX接続失敗、スキップします ({e})")


def speak(path: str) -> None:
        try:
            # afplay is a built-in macOS command to play audio files
            subprocess.run(["afplay", "-v", "2.5", path], check=True)
        finally:
            # Ensure temporary file is deleted
            if os.path.exists(path):
                os.remove(path)
                

if __name__ == "__main__":
    print("Testing TTS (VOICEVOX)...")
    speak("これはテストです。ラジオ局システム、起動準備完了なのだ。")
