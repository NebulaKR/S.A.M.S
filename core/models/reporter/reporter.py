from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.models.announcer.event import Event
from core.models.announcer.news import Media, News
from core.models.reporter.article import Article
from core.models.reporter.prompt_builder import build_article_prompt
from llama_client import query_llm
from utils.id_generator import generate_id


@dataclass
class ReporterConfig:
    min_chars: int = 250
    max_chars: int = 400


class Reporter:
    """각 언론사별 기사를 Event로부터 생성한 뒤, 필요시 News로 변환하는 기능입니다."""

    def __init__(self, config: ReporterConfig | None = None):
        self.config = config or ReporterConfig()

    def generate_articles(
        self,
        *,
        event: Event,
        outlets: List[Media],
        context_events: List[Event] | None = None,
    ) -> List[Article]:
        articles: List[Article] = []
        for outlet in outlets:
            prompt = build_article_prompt(
                event=event,
                outlet=outlet,
                context_events=context_events,
            )

            try:
                article_text = self._postprocess(query_llm(prompt).strip())
                if article_text == "기사 생성에 실패했습니다.":
                    article_text = self._fallback_article(event=event, outlet=outlet)
            except Exception:
                article_text = self._fallback_article(event=event, outlet=outlet)

            articles.append(
                Article(
                    id=generate_id("news"),
                    event_id=event.id,
                    media=outlet.name,
                    body=article_text,
                    stance_score=outlet.bias,
                    confidence=outlet.credibility,
                )
            )
        return articles

    def generate_news(
        self,
        *,
        event: Event,
        outlets: List[Media],
        context_events: List[Event] | None = None,
    ) -> List[News]:
        """Compatibility layer: convert reporter Article outputs to News."""
        return [
            article.to_news()
            for article in self.generate_articles(
                event=event,
                outlets=outlets,
                context_events=context_events,
            )
        ]

    def _postprocess(self, text: str) -> str:
        cleaned = text.replace("```", "").strip()
        if not cleaned:
            return "기사 생성에 실패했습니다."
        if len(cleaned) > self.config.max_chars:
            cleaned = cleaned[: self.config.max_chars].rstrip()
        return cleaned

    def _fallback_article(self, *, event: Event, outlet: Media) -> str:
        direction = "긍정" if event.sentiment >= 0 else "부정"
        return (
            f"{outlet.name}는 '{event.event_type}' 사건을 {direction}적으로 해석했다. "
            f"시장에서는 해당 이슈가 {event.category} 섹터 전반의 변동성을 키울 수 있다는 관측이 나온다. "
            "전문가들은 사실 확인과 후속 지표를 함께 보며 신중히 대응할 필요가 있다고 조언했다."
        )
