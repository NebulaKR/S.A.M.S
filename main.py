from core.models.announcer.announcer import Announcer
from core.models.announcer.event import Event
from core.models.announcer.news import Media

if __name__ == "__main__":
    # 과거 사건 (있으면 전달)
    past_events: list[Event] = []

    # 1) 사건 N개 생성
    announcer = Announcer()
    new_events = announcer.generate_events(
        past_events=past_events,
        count=2,
        allowed_categories=["Tech", "Healthcare", "Policy"]
    )

    # 2) 언론사 목록
    outlets = [
        Media(name="뉴스24", bias=0.2, credibility=0.9),
        Media(name="SNS속보", bias=0.8, credibility=0.3),
    ]

    # 3) 각 사건에 대해 뉴스 생성
    for ev in new_events:
        news_list = announcer.generate_news_for_event(ev, outlets, past_events=past_events)
        print("\n생성된 사건:", ev.event_type, "/", ev.category, "/", ev.duration)
        print("연결된 뉴스 ID:", ev.news_article)
        for n in news_list:
            print(f"\n언론사: {n.media}\n{n.article_text}")

        # 과거 목록에 이번 사건 추가 (다음 라운드 맥락 강화를 위해)
        past_events.append(ev)
