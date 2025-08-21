
from typing import List, Optional
from core.models.announcer.event import Event

def build_event_prompt(
    past_events: Optional[List[Event]] = None,
    count: int = 1,
    allowed_categories: Optional[List[str]] = None,
    language: str = "ko",
    market_context: Optional[str] = None
) -> str:
    """
    사건(Event) 생성을 위한 프롬프트를 구성합니다.
    - past_events: 맥락 유지용 과거 사건들
    - count: 생성할 사건 개수
    - allowed_categories: 허용할 카테고리 화이트리스트 (없으면 자유)
    - language: "ko" 또는 "en" 등 (기본 한글)
    - market_context: 현재 시장 상태 정보
    """
    hist = []
    if past_events:
        for e in past_events[-5:]:  # 최근 5개만 맥락에 포함 (너무 길어지는 것 방지)
            hist.append(
                f"- 제목: {e.event_type} | 카테고리: {e.category} | 감성: {e.sentiment} | 영향: {e.impact_level} | 지속: {e.duration}"
            )
    history_block = "\n".join(hist) if hist else "이전 사건은 없습니다."

    categories_rule = ""
    if allowed_categories:
        cats = ", ".join(allowed_categories)
        categories_rule = f'  "category": "{cats} 중 하나",\n'

    lang_rule = "한국어" if language.lower().startswith("ko") else "English"

    # 시장 컨텍스트 정보 추가
    market_info = ""
    if market_context:
        market_info = f"""

현재 시장 상황:
{market_context}

위 시장 상황을 고려하여 적절한 사건을 생성하세요.
"""

    # JSON 배열만 출력하도록 강하게 요구
    prompt = f"""
다음은 지금까지 발생한 사건들의 요약입니다:
{history_block}{market_info}

위 맥락을 고려하여, 현실적인 새 사건 {count}개를 생성하세요.
응답은 반드시 아래 JSON 배열 형식으로만 출력하세요. (설명/코드블록/주석 금지)

[
  {{
    "event_type": "사건 제목 (간결하게 한국어로)",
    {categories_rule if categories_rule else '  "category": "카테고리",'}
    "sentiment": 감성점수(-1.0~1.0 float),
    "impact_level": 영향수준(1~5 정수),
    "duration": "short" 또는 "mid" 또는 "long"
  }}
]

요구사항:
- 출력은 {lang_rule}로 작성된 JSON만 포함하세요.
- 값 범위를 반드시 지키세요 (sentiment: -1~1, impact_level: 1~5, duration: short/mid/long).
- 허용된 카테고리가 지정되었으면 그 안에서 선택하세요.
- 현재 시장 상황에 맞는 적절한 사건을 생성하세요.
- 사건 제목은 한국어로 간결하게 작성하세요.
- 영어 번역이나 번역 표시를 포함하지 마세요.
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

[중요 규칙]
- 한국어로만 작성하세요. 영어 번역이나 번역 표시를 포함하지 마세요.
- 코드, JSON, 기술적 파라미터를 포함하지 마세요.
- 순수한 뉴스 기사 형태로만 작성하세요.
- 언론사 이름은 기사 내용에 포함하지 마세요.
- 사건 정보의 기술적 세부사항은 일반 독자가 이해할 수 있는 언어로 변환하세요.
""".strip()
    return prompt

