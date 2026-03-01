from __future__ import annotations

from dataclasses import dataclass

from core.models.announcer.news import News


@dataclass
class Article:
    """Reporter가 생성한 기사 도메인 객체 (News와 구분되는 생성 단계 산출물)."""

    id: str
    event_id: str
    media: str
    body: str
    stance_score: float
    confidence: float

    def to_news(self) -> News:
        """기존 파이프라인 호환을 위해 News 객체로 변환."""
        return News(id=self.id, media=self.media, article_text=self.body)
