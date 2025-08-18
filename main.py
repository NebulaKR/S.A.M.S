from core.models.announcer.announcer import Announcer
from core.models.announcer.event import Event
from core.models.announcer.news import Media
from utils.id_generator import generate_id
from core.models.config.generator import get_internal_params
from core.models.coach.coach import Coach
from core.models.main_model import main_model

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

    # 내부 파라미터 생성 및 코치 가중치 산출
    params = get_internal_params(seed=7)
    coach = Coach(params)
    weights = coach.adjust_weights()

    # 아나운서 사용 (LLM 비가용 시에도 진행)
    announcer = Announcer()
    try:
        news_list = announcer.generate_news_for_event(new_event, outlets, past_events)
    except Exception as e:
        print(f"⚠️ Announcer 호출 실패, 더미로 진행: {e}")
        news_list = []

    # 결과 출력
    print("\n📢 생성된 사건:")
    print(f"- 제목: {new_event.event_type}")
    print(f"- 뉴스 기사 ID 목록: {new_event.news_article}")

    print("\n📰 생성된 뉴스 기사들:")
    for news in news_list:
        print(f"\n- 언론사: {news.media}")
        print(news.article_text)

    # 뉴스 임팩트 간단 추정: sentiment(-1~1)→[0,1] 변환 후 impact_level(1~5) 가중
    sentiment_score = max(0.0, min(1.0, (new_event.sentiment + 1.0) / 2.0))
    impact_scale = max(0.0, min(1.0, new_event.impact_level / 5.0))
    news_impact = round(sentiment_score * impact_scale, 3)

    # 메인 모델 계산
    result = main_model(weights, params, {"news_impact": news_impact}, base_price=100.0)

    print("\n🧮 메인 모델 계산:")
    print(f"- 가중치: {weights}")
    print(f"- 추정 news_impact: {news_impact}")
    print(f"- delta: {result['delta']}, price: {result['price']}")
