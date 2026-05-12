import requests
import subprocess
import tempfile
import os
from janome.tokenizer import Tokenizer

# Janome Tokenizerの初期化
tokenizer = Tokenizer()
SPEAKER_ID = 3  # ずんだもん
SPEED_SCALE = 1.3  # 読み上げ速度 (1.0が標準、1.3〜1.5が聞き取りやすく速い)

def _preprocess_text(text: str) -> str:
    """漢字混じりのテキストを、分かち書きされた読み（平仮名/カタカナ）に変換する"""
    try:
        processed = []
        for token in tokenizer.tokenize(text):
            # 読み（カタカナ）を取得。取得できない場合は元の表層形を使用
            reading = token.reading if token.reading != '*' else token.surface
            processed.append(reading)
        
        # スペースで区切ることでVOICEVOXが自然な「間」を作れるようにする
        return " ".join(processed)
    except Exception as e:
        print(f"[tts] Janomeでの解析に失敗しました: {e}")
        return text

def speak(text: str) -> None:
    base_url = "http://localhost:50021"
    
    # 読みと分かち書きを自動生成
    reading_text = text
    #reading_text = _preprocess_text(text)
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
            
        try:
            # afplay is a built-in macOS command to play audio files
            subprocess.run(["afplay", tmp_path], check=True)
        finally:
            # Ensure temporary file is deleted
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        print(f"[tts] VOICEVOX接続失敗、スキップします ({e})")

if __name__ == "__main__":
    print("Testing TTS (VOICEVOX)...")
    speak("これはテストです。ラジオ局システム、起動準備完了なのだ。")
