# AGENTS.md — 自作ラジオ局システム 実装実態記録 (YTM Edition)

## プロジェクト概要

ローカル環境（macOS / M4 Max）で動作する自動ラジオ局システム。
外部有料API（Spotify等）を一切使用せず、ブラウザ自動操作とローカルLLMを組み合わせて動作する。

**処理フロー:**
```
Python スケジューラー (main.py)
  → NHK RSS + 時刻でコンテキスト生成 (context_builder.py)
  → LM Studio (ローカルLLM) でニュース要約 + MC台本生成 (llm_director.py)
  → Selenium で Chrome を操作し YouTube Music 再生制御 (ytm_player.py)
      - 専用プロファイル使用、フェードイン/アウト実装
  → VOICEVOX で読み上げ (tts.py)
      - afplay (macOS) を使用した再生
```

---

## サービス構成

| サービス | 接続先 | 役割 |
|---|---|---|
| LM Studio | `localhost:1234` | OpenAI互換サーバー。台本執筆を担当。 |
| VOICEVOX | `localhost:50021` | 音声合成。ずんだもんを使用。 |
| Chrome | `Selenium` | YouTube Music の再生。専用プロファイル `chrome_profile` を使用。 |

---

## 実装実態詳細

### 1. context_builder.py
- `get_context() -> dict`
- 時刻に基づき `mood` を決定。
- NHK の RSS フィードから最新ヘッドラインを取得。
- `NewsManager` クラスでニュースを管理し、リングキュー形式で提供。

### 2. llm_director.py
- `get_direction(context, previous_track)`
- ニュースの要約と、それに基づくパーソナライズされた話題を含む MC 台本を生成。
- 直前の曲への言及を含めるロジック。

### 3. ytm_player.py
- Selenium/Chrome を使用。
- **専用プロファイル:** `chrome_profile/` を使用し、ログイン状態を維持。
- **再生制御:** 
    - 特定のチャートプレイリスト (`OLAK5uy_nMa6r07BbcC_Q8PrrS1CVHH2aGJRIkWu0`) をデフォルトで使用。
    - ランダムなプレイリストの選択と再生。
- **音響制御:** JavaScript で `video.volume` を操作し、フェードイン（3秒）とフェードアウト（5秒）を実現。
- **停止機能:** `stop()` で音量を 0.0 に固定し、ブラウザの一時停止ボタンを叩く。

### 4. tts.py
- **VOICEVOX 連携:** 指定された話速 (`SPEED_SCALE = 1.0`) で音声を合成。
- **再生:** macOS 標準の `afplay` を使用。一時ファイルを生成して再生後に削除。

### 5. main.py (Orchestrator)
- **放送サイクル:** 1セグメント = 「MCトーク」 + 「楽曲 1 曲再生」。
- **並列処理:** 音楽再生中に `threading` を利用して「次のセグメント」の MC 台本と音声をバックグラウンドで準備。
- **無限ループ:** 各セグメントの間に最新ニュースを取得し直す。

---

## 依存ライブラリ (`requirements.txt`)

```text
feedparser
openai
requests
selenium
webdriver-manager
```

---

## 運用上の注意

1. **初回起動時:**
   `make run` で起動した Chrome ウィンドウにて、YouTube Music へのログインを手動で行うこと。これにより Premium 機能等が有効になる。
2. **LM Studio / VOICEVOX:**
   実行前に各サーバーが起動している必要がある。
3. **音量制御:**
   システム音量ではなく、ブラウザ内の動画音量を直接操作するため、システム全体の音設定を汚さない。
