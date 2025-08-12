from core.models.announcer.announcer import Announcer

if __name__ == "__main__":
    past = [
        "정부, 반도체 산업 규제 완화 발표",
        "대형 IT기업 A, 신규 AI 칩 공개",
        "소비 심리 회복, 주식시장 반등 조짐"
    ]

    announcer = Announcer()
    event = announcer.generate_event(past)

    print(" 생성된 사건:")
    print(event)
