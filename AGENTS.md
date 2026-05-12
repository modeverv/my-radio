# AGENTS.md — 自作ラジオ局システム 実装実態記録 (YTM Edition)

## プロジェクト概要

ローカル環境（macOS / M4 Max）で動作する自動ラジオ局システム。
外部有料API（Spotify等）を一切使用せず、ブラウザ自動操作とローカルLLMを組み合わせて動作する。

**処理フロー:**
```
Python スケジューラー (main.py)
  → RSS (BBC/CNN/NHK) + 時刻でコンテキスト生成 (context_builder.py)
  → YouTube Music 日本チャートから候補曲リスト取得 (youtube_client.py)
  → LM Studio (ローカルLLM) でニュース要約 + 選曲 + MC台本生成 (llm_director.py)
  → Selenium で Chrome を操作し YouTube Music 再生制御 (ytm_player.py)
      - 専用プロファイル使用、フェードイン/アウト実装
  → Janome で台本の形態素解析を行い、VOICEVOX で読み上げ (tts.py)
      - 話速調整 (1.3x) 実装済み
```

---

## サービス構成

| サービス | 接続先 | 役割 |
|---|---|---|
| LM Studio | `localhost:1234` | OpenAI互換サーバー。台本執筆と選曲を担当。 |
| VOICEVOX | `localhost:50021` | 音声合成。ずんだもんを使用。 |
| Chrome | `Selenium` | YouTube Music の再生。専用プロファイル `chrome_profile` を使用。 |
| Janome | `Library` | 日本語の形態素解析・読み・分かち書き生成。 |

---

## 実装実態詳細

### 1. context_builder.py
- `get_context() -> dict`
- 時刻に基づき `mood` を決定。
- BBC, CNN, NHK の RSS から最新ヘッドラインを取得。

### 2. youtube_client.py
- `ytmusicapi` ライブラリを使用。
- YouTube Music の最新日本チャート（または検索によるフォールバック）から候補曲を 15 曲抽出。
- 認証不要（パブリックデータを使用）。

### 3. llm_director.py
- `get_direction(context, candidates)`
- ニュースの要約と、それに基づくパーソナライズされた話題を含む MC 台本を生成。
- 候補から 2 曲を厳選。

### 4. ytm_player.py
- Selenium/Chrome を使用。
- **専用プロファイル:** `chrome_profile/` を使用し、ログイン状態を維持。
- **コンテキスト認識再生:**
    - プレイリスト画面なら直接クリック。
    - それ以外ならグローバル検索を実行。
- **音響制御:** JavaScript で `video.volume` を操作し、フェードイン（3秒）とフェードアウト（5秒）を実現。
- **停止機能:** `stop()` で音量を 0.0 に固定。

### 5. tts.py
- **Janome 統合:** LLM のテキストを形態素解析し、読みと分かち書きを自動生成。
- **VOICEVOX 連携:** 指定された話速 (`SPEED_SCALE = 1.3`) で音声を合成。
- **再生:** macOS 標準の `afplay` を使用。

### 6. main.py (Orchestrator)
- **放送サイクル:** 1セグメント = 「MCトーク」 + 「楽曲 2 曲再生」。
- **無限ループ:** 各セグメントの間に最新ニュースを取得し直す。

---

## 依存ライブラリ (`requirements.txt`)

```text
feedparser
openai
requests
python-dotenv
ytmusicapi
selenium
webdriver-manager
janome
```

---

## 運用上の注意

1. **初回起動時:**
   `make run` で起動した Chrome ウィンドウにて、YouTube Music へのログインを手動で行うこと。これにより Premium 機能等が有効になる。
2. **LM Studio / VOICEVOX:**
   実行前に各サーバーが起動している必要がある。
3. **音量制御:**
   システム音量ではなく、ブラウザ内の動画音量を直接操作するため、システム全体の音設定を汚さない。
