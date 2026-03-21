from __future__ import annotations

from typing import List

from core.models.announcer.event import Event
from core.models.announcer.news import Media


def build_article_prompt(
    *,
    event: Event,
    outlet: Media,
    context_events: List[Event] | None = None,
) -> str:
    """Reporter LLM을 위한 엄격한 기사 생성 프롬프트를 만듭니다."""
    context_events = context_events or []

    lines: list[str] = [
        "당신은 금융 뉴스 리포터입니다.",
        "사건(Event)과 언론사 성향을 기반으로 기사 본문을 작성하세요.",
        "JSON이나 코드블록 없이 기사 본문 텍스트만 출력하세요.",
        "",
        "[현재 사건]",
        f"- 사건 ID: {event.id}",
        f"- 제목: {event.event_type}",
        f"- 카테고리: {event.category}",
        f"- 감성(sentiment): {event.sentiment}",
        f"- 영향도(impact_level): {event.impact_level}",
        "",
        "[언론사 성향]",
        f"- 언론사: {outlet.name}",
        f"- 편향(bias): {outlet.bias} (-1 보수 ~ +1 진보)",
        f"- 신뢰도(credibility): {outlet.credibility} (0~1)",
        "",
        "[작성 규칙]",
        "1) 기사 길이 250~400자",
        "2) 금융 기사 톤으로 작성",
        "3) bias 값에 따라 해석 프레임과 강조점을 다르게",
        "4) credibility 값이 낮을수록 추정/전망성 표현을 더 자주 사용",
        "5) 사실(Event)과 의견(해석)을 분리해서 서술",
    ]

    if context_events:
        lines += ["", "[최근 맥락 사건]"]
        for idx, ctx in enumerate(context_events[-5:], start=1):
            lines.append(
                f"{idx}. {ctx.event_type} / {ctx.category} / sentiment={ctx.sentiment}"
            )

    return "\n".join(lines)
