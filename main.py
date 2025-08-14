from core.models.announcer.announcer import Announcer
from core.models.announcer.event import Event
from core.models.announcer.news import Media
from utils.id_generator import generate_id

if __name__ == "__main__":
    # 이전 사건들 (테스트용)
    past_events = [
        Event(
            id="event-001",
            event_type="AI 반도체 발표",
            category="Tech",
            sentiment=0.7,
            impact_level=4,
            duration="mid",
            news_article=[]
        ),
        Event(
            id="event-002",
            event_type="금리 인하 발표",
            category="Macro",
            sentiment=0.5,
            impact_level=3,
            duration="short",
            news_article=[]
        )
    ]

    # 테스트용 언론사 목록
    outlets = [
        Media(name="파이낸셜잉글리시", bias=-0.7, credibility=0.4),
        Media(name="뉴스24", bias=0.2, credibility=0.9)
    ]

    # 새 사건 정의
    new_event = Event(
        id=generate_id("event"),
        event_type="AI 헬스케어 플랫폼 출시",
        category="Healthcare",
        sentiment=0.8,
        impact_level=4,
        duration="mid",
        news_article=[]
    )

    # 아나운서 사용
    announcer = Announcer()
    news_list = announcer.generate_news_for_event(new_event, outlets, past_events)

    # 결과 출력
    print("\n📢 생성된 사건:")
    print(f"- 제목: {new_event.event_type}")
    print(f"- 뉴스 기사 ID 목록: {new_event.news_article}")

    print("\n📰 생성된 뉴스 기사들:")
    for news in news_list:
        print(f"\n- 언론사: {news.media}")
        print(news.article_text)
