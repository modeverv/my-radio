# My Radio Station System (YTM Edition)

ローカル環境（macOS）で動作する、自動ラジオ局システムです。RSSから最新ニュースを取得し、YouTube Music の日本チャートから選曲。ローカルLLMでMC台本を生成し、VOICEVOXで読み上げながらブラウザ（Selenium）で楽曲を再生します。
＜開発中＞
初っ端が不安定

## システム構成

- **Scheduler:** Python (`main.py`)
- **Context:** RSS News (BBC/CNN/NHK) + Time-based Mood
- **Selection:** YouTube Music Japan Charts (`youtube_client.py`)
- **Director:** LM Studio (Local LLM - MC Script & Song Selection)
- **Player:** YouTube Music via Selenium/Chrome (`ytm_player.py`)
- **TTS:** VOICEVOX (Zundamon)

## 準備するもの

1.  **LM Studio:** OpenAI互換サーバーを `localhost:1234` で起動し、モデルをロードしておいてください。
2.  **VOICEVOX:** アプリを起動しておいてください（`localhost:50021`）。
3.  **Google Chrome:** Seleniumによる操作に使用します。

## セットアップ

1.  依存ライブラリのインストール:
    ```bash
    make install
    ```

2.  **専用プロファイルの作成とログイン:**
    初回起動時（`make run`）に専用の Chrome ウィンドウが立ち上がります。そのウィンドウで YouTube Music にログインしてください。一度ログインすれば、次回以降は Premium 機能や広告なしの状態が維持されます。

## 使い方

### 実行
```bash
make run
```
1セグメント（MCトーク + 楽曲2曲）のサイクルで無限ループ実行されます。


## 主な機能

- **ニュース要約 MC:** 最新のヘッドラインを LLM が要約し、あなたなりの視点で語るトークを生成します。
- **読み間違い防止:** VOICEVOX 用に平仮名・カタカナ専用の台本（`mc_reading`）を生成し、スムーズな読み上げを実現します。
- **ビジュアル再生:** ブラウザが自動的に日本チャートを表示し、ランクインしている楽曲をクリックして再生します。
- **オーディオ演出:** 楽曲の開始時に3秒のフェードイン、終了時に5秒のフェードアウトを自動で行います。

## ディレクトリ構成
- `main.py`: 全体のオーケストレーション。
- `context_builder.py`: ニュースと時刻からコンテキスト生成。
- `youtube_client.py`: YouTube Music から候補曲を取得。
- `llm_director.py`: LLM を用いた要約・選曲・台本作成。
- `ytm_player.py`: Selenium によるブラウザ操作と音響制御。
- `tts.py`: VOICEVOX による音声合成。
- `chrome_profile/`: 専用のブラウザプロファイル（自動生成）。
- `tests/`: ユニットテスト。

## 注意事項
- **再生時間:** デフォルトで30秒（テスト用）に設定されています。`main.py` の `PLAY_DURATION_SEC` で変更可能です。
- **Chrome の競合:** 専用プロファイルを使用しているため、普段使いの Chrome と同時に起動可能です。
- **外部 API:** Spotify API 等の外部有料 API は一切使用しません。
