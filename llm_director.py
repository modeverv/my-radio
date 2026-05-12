import json
from openai import OpenAI

# LM Studio configuration
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

SYSTEM_PROMPT = """あなたはラジオ局のディレクター兼放送作家です。
与えられたコンテキスト（時刻、ニュース、気分）と候補曲リストを読み、以下のJSONのみを返してください。
特にニュースの内容については、ただ読み上げるのではなく、あなたなりの視点で短く要約し、リスナーに語りかけるような話題としてMCトークに組み込んでください。
マークダウンのコードブロックや説明文は一切不要です。JSONのみ。

{
  "playlist": [{"title": "曲名", "artist": "アーティスト名"}, {"title": "曲名", "artist": "アーティスト名"}],
  "mc_script": "MCトーク台本（自然な漢字混じりの日本語、300〜400字程度）",
  "show_title": "このコーナーのタイトル"
}"""

USER_PROMPT_TEMPLATE = """時刻: {time} ({day_of_week})
気分: {mood}
【最新ニュース（ヘッドライン）】
{headlines}

【候補曲リスト】
{candidates_list}

上記ニュースの内容を要約し、音楽へ繋げるMC台本（漢字混じりの自然な日本語）を作成してください。
候補曲からこの後の放送にふさわしい曲を「ちょうど2曲」選び、選曲理由も含めてください。"""

FALLBACK_DIRECTION = {
    "playlist": [{"title": "Jazz", "artist": ""}],
    "mc_script": "こんにちは、ラジオをお楽しみください。",
    "show_title": "デフォルト放送"
}

def get_direction(context: dict, candidates: list[dict]) -> dict:
    # Format candidates list for prompt
    candidates_str = "\n".join([f"{i+1}. {c['title']} / {c['artist']}" for i, c in enumerate(candidates)])
    
    # Headlines summary
    headlines_str = ", ".join(context.get("headlines", [])[:3])
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        time=context.get("time"),
        day_of_week=context.get("day_of_week"),
        mood=context.get("mood"),
        headlines=headlines_str,
        candidates_list=candidates_str
    )
    
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Basic cleaning in case the LLM includes markdown code blocks
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            elif content.startswith("```"):
                content = content.replace("```", "", 2).strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"[llm_director] Error on attempt {attempt + 1}: {e}")
            
    print("[llm_director] Failed after 2 attempts. Using fallback direction.")
    return FALLBACK_DIRECTION

if __name__ == "__main__":
    # Test context and candidates
    test_ctx = {
        "time": "07:32",
        "day_of_week": "Monday",
        "mood": "morning_calm",
        "headlines": ["Headline 1", "Headline 2", "Headline 3"]
    }
    test_candidates = [
        {"title": "Song A", "artist": "Artist 1"},
        {"title": "Song B", "artist": "Artist 2"},
        {"title": "Song C", "artist": "Artist 3"},
        {"title": "Song D", "artist": "Artist 4"},
        {"title": "Song E", "artist": "Artist 5"},
    ]
    direction = get_direction(test_ctx, test_candidates)
    print(json.dumps(direction, indent=2, ensure_ascii=False))
