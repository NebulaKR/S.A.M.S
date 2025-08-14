from dataclasses import dataclass, field
from typing import List

@dataclass
class Event:
    id: str  # 사건 ID (예: "event-abc123")
    event_type: str  # 사건 이름 또는 종류 (예: "AI 칩 수요 급증")
    category: str  # 산업/정책/사회 등 카테고리
    sentiment: float  # 사건에 대한 감성 점수 (-1 ~ +1)
    impact_level: int  # 사건의 영향 강도 (1~5)
    duration: str  # 사건 지속 기간 (예: "short", "mid", "long")
    news_article: List[str] = field(default_factory=list)  # 이 사건을 기반으로 작성된 뉴스들의 ID 목록
