from dataclasses import dataclass, asdict
from core.models.announcer.event import Event

@dataclass
class News:
    id: str  # 뉴스 ID (예: "news-xyz456")
    media: str  # 보도 언론사 이름 (예: "뉴스라이브", "SNS속보")
    article_text: str  # 실제 뉴스 본문 내용
    
    def to_dict(self):
        """News 객체를 딕셔너리로 변환"""
        return asdict(self)

@dataclass
class Media:
    #id: str  # 언론사 ID (예: "news-xyz456")
    name: str  # 언론사 이름 (예: "뉴스라이브", "SNS속보")
    bias: float  # 언론의 성향 (-1: 보수, 0: 중립, +1: 진보)
    credibility: float  # 언론의 신뢰도 (0~1)