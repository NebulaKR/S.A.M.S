from core.models.announcer.event import Event
from core.models.announcer.news import News, Media
from utils.id_generator import generate_id
from llama_client import query_llm  # LLaMA용 LLM wrapper

class Announcer:
    def generate_news_for_event(
        self,
        event: Event,
        outlets: list[Media],
        past_events: list[Event] = None
    ) -> list[News]:
        """주어진 사건에 대해 각 언론사별 뉴스 기사를 생성하고 연결한다."""

        news_list = []

        for outlet in outlets:
            article_text = self.generate_news(event, outlet, past_events)
            news_id = generate_id("news")

            news = News(
                id=news_id,
                media=outlet.name,
                article_text=article_text
            )

            news_list.append(news)
            event.news_article.append(news_id)  # 문자열 ID만 추가

        return news_list

    def generate_news(
        self,
        current_event: Event,
        outlet: Media,
        past_events: list[Event] = None
    ) -> str:
        """사건과 언론사 정보를 기반으로 뉴스 기사 텍스트 생성"""

        prompt = "다음은 지금까지 발생한 사건들의 요약입니다:\n\n"

        if past_events:
            for i, ev in enumerate(past_events, 1):
                prompt += (
                    f"{i}. 사건명: {ev.event_type} / 카테고리: {ev.category} / "
                    f"감성: {ev.sentiment} / 영향 수준: {ev.impact_level} / 지속: {ev.duration}\n"
                )
        else:
            prompt += "이전 사건은 없습니다.\n"

        prompt += "\n이후, 현재 사건은 다음과 같습니다:\n\n"
        prompt += (
            f"[사건 정보]\n"
            f"- 제목: {current_event.event_type}\n"
            f"- 카테고리: {current_event.category}\n"
            f"- 감성 점수: {current_event.sentiment}\n"
            f"- 영향 수준: {current_event.impact_level}\n"
            f"- 지속 기간: {current_event.duration}\n\n"
        )

        prompt += (
            "이 사건에 대해, 아래 언론사의 성향과 신뢰도를 반영한 뉴스 기사를 생성하세요:\n\n"
            f"[언론사 정보]\n"
            f"- 이름: {outlet.name}\n"
            f"- 성향 (bias): {outlet.bias} (-1: 보수, 0: 중립, +1: 진보)\n"
            f"- 신뢰도 (credibility): {outlet.credibility} (0~1)\n\n"
            f"[출력 형식]\n"
            f"뉴스 기사 본문만 출력하세요.\n"
            f"과장, 왜곡, 미화 여부는 언론 성향과 신뢰도에 따라 판단해 작성하세요.\n"
        )

        return query_llm(prompt).strip()
