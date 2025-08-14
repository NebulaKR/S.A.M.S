# core/models/announcer/prompt_builder.py

def build_event_prompt(past_events: list[str]) -> str: # 이벤트 프롬프트 빌더 함수
    """
    사건(Event) 생성을 위한 LLM 프롬프트 문자열을 생성합니다.

    Parameters:
        past_events: 과거에 발생한 사건 리스트

    Returns:
        str: LLM에 전달할 사건 생성 프롬프트
    """
    history_text = "\n".join(f"- {e}" for e in past_events)

    prompt = f"""
당신은 다음 사건을 예측하는 금융/사회 전문가입니다.
다음은 과거에 발생한 사건 목록입니다:

{history_text}

위 사건들을 참고하여, 새로운 사건 1개를 아래의 JSON 형식으로 생성하세요:

출력 형식:
{{
  "event_type": "사건 제목",
  "category": "Tech",
  "sentiment": 0.6,
  "impact_level": 3,
  "duration": "mid"
}}

주의:
- JSON 외의 추가 텍스트는 출력하지 마세요.
- 사건은 현실적인 경제, 산업, 정치 흐름에 기반해야 합니다.
""".strip()
    return prompt

def build_news_prompt(event_data: dict, outlet_info: dict) -> str: # 뉴스 프롬프트 빌더
    """
    뉴스 생성용 프롬프트 생성 (특정 언론 성향 반영)

    Parameters:
        event_data: 생성된 사건 정보 (딕셔너리 형태)
        outlet_info: 언론사 정보 (bias, credibility 등 포함)

    Returns:
        str: 뉴스 기사 생성을 위한 프롬프트
    """
    prompt = f"""
다음은 특정 사건에 대한 정보입니다:

[사건 정보]
- 제목: {event_data['event_type']}
- 카테고리: {event_data['category']}
- 감성 점수: {event_data['sentiment']}
- 영향 수준: {event_data['impact_level']}
- 지속 기간: {event_data['duration']}

이 사건에 대해, 아래 언론사의 성향과 신뢰도를 반영한 뉴스 기사를 생성하세요:

[언론사 정보]
- 이름: {outlet_info['name']}
- 성향 (bias): {outlet_info['bias']} (-1: 보수, 0: 중립, +1: 진보)
- 신뢰도 (credibility): {outlet_info['credibility']} (0~1)

[출력 형식]
뉴스 기사 본문만 출력하세요.  
과장, 왜곡, 미화 여부는 언론 성향과 신뢰도에 따라 판단해 작성하세요.
""".strip()
    return prompt

