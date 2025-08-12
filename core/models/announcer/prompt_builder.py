def build_prompt(past_events: list[str]) -> str:
    context = "\n".join(f"{i+1}. {e}" for i, e in enumerate(past_events))
    prompt = f"""
다음은 과거에 발생한 사건들입니다:

{context}

이제 이어질 수 있는 사건을 하나 생성하고, 그에 대한 뉴스 기사도 작성해주세요.
다음의 예시 JSON 형식으로 출력해주세요. 다른 말은 절대 하지 마세요.

{{
  "event_type": "이벤트 이름",
  "category": "산업 카테고리 (예: Tech, Policy, Finance)",
  "sentiment": 숫자 (-1.0 ~ 1.0),
  "impact_level": 정수 (1~5),
  "duration": "short" 또는 "mid" 또는 "long",
  "news_article": "뉴스 기사 본문 (한 문단)"
}}
"""
    return prompt.strip()