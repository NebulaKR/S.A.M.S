#!/usr/bin/env python3
"""
뉴스 기사 생성 기능 테스트 스크립트
파이어스토어에서 이벤트 로그를 조회하여 뉴스 기사를 생성하는 기능을 테스트합니다.
"""

import time
import sys
import os
from pathlib import Path
import environ

# 환경 변수 로드
environ.Env.read_env(str(Path(__file__).resolve().parent / ".env"))

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models.simulation_engine import SimulationEngine, SimulationSpeed
from core.models.announcer.news import Media
from utils.logger import list_event_logs, get_news_articles_for_event


def on_price_change(stock_price):
    """주가 변화 콜백"""
    print(f"📈 {stock_price.ticker}: ₩{stock_price.current_price:,.0f} "
          f"({stock_price.change_rate:+.2%})")


def on_event_occur(sim_event):
    """이벤트 발생 콜백"""
    print(f"📰 이벤트 발생: {sim_event.event.event_type} "
          f"(영향 종목: {len(sim_event.affected_stocks)}개)")


def on_news_update(news):
    """뉴스 업데이트 콜백"""
    print(f"📰 뉴스 생성: {news.media} - {news.id}")


def test_news_generation_for_existing_events():
    """기존 이벤트들에 대한 뉴스 기사 생성 테스트"""
    print("🔍 기존 이벤트들에 대한 뉴스 기사 생성 테스트")
    print("=" * 60)
    
    # 시뮬레이션 ID 설정 (실제 저장된 시뮬레이션 ID로 변경)
    sim_id = "default-sim"  # 실제 시뮬레이션 ID로 변경하세요
    
    # 1. 기존 이벤트 로그 조회
    print(f"📋 시뮬레이션 '{sim_id}'의 이벤트 로그 조회 중...")
    event_logs = list_event_logs(sim_id, limit=10)
    
    if not event_logs:
        print("❌ 이벤트 로그를 찾을 수 없습니다.")
        print("먼저 시뮬레이션을 실행하여 이벤트를 생성해주세요.")
        return
    
    print(f"✅ {len(event_logs)}개의 이벤트 로그를 찾았습니다.")
    
    # 2. 첫 번째 이벤트에 대한 뉴스 기사 생성 테스트
    first_event = event_logs[0]
    event_id = first_event.get("event", {}).get("id", "unknown")
    event_type = first_event.get("event", {}).get("event_type", "unknown")
    
    print(f"\n📰 이벤트 '{event_type}' (ID: {event_id})에 대한 뉴스 기사 생성 테스트")
    print("-" * 50)
    
    # 3. 언론사 설정 (테스트용으로 일부만 선택)
    test_outlets = [
        Media(name="조선일보", bias=-0.8, credibility=0.7),      # 보수적
        Media(name="한겨레", bias=0.7, credibility=0.8),         # 진보적
        Media(name="매일경제", bias=0.0, credibility=0.8),       # 중립 (경제 전문)
        Media(name="KBS", bias=0.0, credibility=0.9),            # 중립 (방송)
    ]
    
    # 4. Announcer를 사용하여 뉴스 기사 생성
    from core.models.announcer.announcer import Announcer
    announcer = Announcer()
    
    try:
        news_list = announcer.generate_news_for_event_from_firestore(
            sim_id=sim_id,
            event_id=event_id,
            outlets=test_outlets,
            context_events_limit=3
        )
        
        print(f"✅ {len(news_list)}개의 뉴스 기사가 생성되었습니다.")
        
        # 5. 생성된 뉴스 기사 출력
        for i, news in enumerate(news_list, 1):
            print(f"\n📰 뉴스 {i}: {news.media}")
            print(f"   ID: {news.id}")
            print(f"   내용: {news.article_text[:100]}...")
            print("-" * 30)
        
        # 6. 파이어스토어에서 저장된 뉴스 기사 조회
        print(f"\n💾 파이어스토어에서 저장된 뉴스 기사 조회...")
        saved_news = get_news_articles_for_event(sim_id, event_id)
        print(f"✅ 파이어스토어에 {len(saved_news)}개의 뉴스 기사가 저장되었습니다.")
        
        for i, news_data in enumerate(saved_news, 1):
            print(f"\n💾 저장된 뉴스 {i}:")
            print(f"   언론사: {news_data.get('media_name', 'N/A')}")
            print(f"   생성 시간: {news_data.get('created_at', 'N/A')}")
            print(f"   내용: {news_data.get('article_text', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"❌ 뉴스 기사 생성 중 오류: {e}")


def test_multiple_events_news_generation():
    """여러 이벤트에 대한 일괄 뉴스 기사 생성 테스트"""
    print("\n🔍 여러 이벤트에 대한 일괄 뉴스 기사 생성 테스트")
    print("=" * 60)
    
    sim_id = "default-sim"  # 실제 시뮬레이션 ID로 변경하세요
    
    # 1. 이벤트 로그 조회
    event_logs = list_event_logs(sim_id, limit=5)
    
    if not event_logs:
        print("❌ 이벤트 로그를 찾을 수 없습니다.")
        return
    
    # 2. 이벤트 ID 목록 추출
    event_ids = []
    for event_log in event_logs:
        event_id = event_log.get("event", {}).get("id")
        if event_id:
            event_ids.append(event_id)
    
    if not event_ids:
        print("❌ 유효한 이벤트 ID를 찾을 수 없습니다.")
        return
    
    print(f"📋 {len(event_ids)}개의 이벤트에 대한 뉴스 기사 생성 시작...")
    
    # 3. 테스트용 언론사 설정
    test_outlets = [
        Media(name="조선일보", bias=-0.8, credibility=0.7),
        Media(name="한겨레", bias=0.7, credibility=0.8),
        Media(name="매일경제", bias=0.0, credibility=0.8),
    ]
    
    # 4. 일괄 뉴스 기사 생성
    from core.models.announcer.announcer import Announcer
    announcer = Announcer()
    
    try:
        results = announcer.generate_news_for_multiple_events(
            sim_id=sim_id,
            event_ids=event_ids,
            outlets=test_outlets,
            context_events_limit=3
        )
        
        print(f"\n✅ 일괄 뉴스 기사 생성 완료!")
        
        # 5. 결과 요약
        total_news = 0
        for event_id, news_list in results.items():
            print(f"   이벤트 {event_id}: {len(news_list)}개 뉴스 기사")
            total_news += len(news_list)
        
        print(f"\n📊 총 {total_news}개의 뉴스 기사가 생성되었습니다.")
        
    except Exception as e:
        print(f"❌ 일괄 뉴스 기사 생성 중 오류: {e}")


def test_simulation_with_news_generation():
    """뉴스 기사 생성이 포함된 시뮬레이션 테스트"""
    print("\n🚀 뉴스 기사 생성이 포함된 시뮬레이션 테스트")
    print("=" * 60)
    
    # 초기 시장 데이터 설정
    initial_data = {
        "stocks": {
            "005930": {"price": 79000, "volume": 1000000, "base_price": 79000},  # 삼성전자
            "000660": {"price": 45000, "volume": 500000, "base_price": 45000},   # SK하이닉스
            "005380": {"price": 180000, "volume": 300000, "base_price": 180000}, # 현대차
            "005490": {"price": 85000, "volume": 400000, "base_price": 85000},   # 기아
            "035420": {"price": 220000, "volume": 200000, "base_price": 220000}, # NAVER
        },
        "market_params": {
            "public": {
                "risk_appetite": 0.3, 
                "news_sensitivity": 0.7,
                "consumer_index": 55.0
            },
            "government": {
                "policy_direction": 0.2,
                "interest_rate": 3.25,
                "tax_policy": -0.1,
                "industry_support": {
                    "AI": 0.6,
                    "Green": 0.3,
                    "반도체": 0.8
                }
            },
            "company": {
                "orientation": 0.1, 
                "rnd_focus": 0.4
            }
        }
    }
    
    # 시뮬레이션 엔진 초기화
    engine = SimulationEngine(initial_data)
    
    # 뉴스 기사 생성 활성화
    engine.enable_news_generation(True)
    
    # 콜백 함수 등록
    engine.add_callback("price_change", on_price_change)
    engine.add_callback("event_occur", on_event_occur)
    engine.add_callback("news_update", on_news_update)
    
    # 시뮬레이션 시작
    print("시뮬레이션 시작...")
    engine.start()
    
    try:
        # 시뮬레이션 루프 (2분간 실행)
        for i in range(120):  # 2분 = 120초
            engine.update()
            
            # 10초마다 현재 상태 출력
            if i % 10 == 0:
                state = engine.get_current_state()
                print(f"\n⏰ 시뮬레이션 시간: {state['simulation_time']}")
                print(f"📰 총 뉴스 수: {len(engine.news_history)}")
                print(f"📊 총 이벤트 수: {len(engine.events_history)}")
                print("-" * 40)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단됨")
    
    # 시뮬레이션 정지
    engine.stop()
    
    # 최종 결과 출력
    print("\n📋 시뮬레이션 결과 요약")
    print("=" * 60)
    print(f"총 이벤트 수: {len(engine.events_history)}")
    print(f"총 뉴스 기사 수: {len(engine.news_history)}")
    
    if engine.news_history:
        print(f"\n📰 최근 생성된 뉴스 기사들:")
        for i, news in enumerate(engine.news_history[-3:], 1):
            print(f"   {i}. {news.media}: {news.article_text[:50]}...")


def main():
    """메인 함수"""
    print("🎯 뉴스 기사 생성 기능 테스트")
    print("=" * 60)
    
    # 테스트 옵션 선택
    print("테스트 옵션을 선택하세요:")
    print("1. 기존 이벤트에 대한 뉴스 기사 생성 테스트")
    print("2. 여러 이벤트 일괄 뉴스 기사 생성 테스트")
    print("3. 뉴스 기사 생성이 포함된 시뮬레이션 테스트")
    print("4. 모든 테스트 실행")
    
    try:
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            test_news_generation_for_existing_events()
        elif choice == "2":
            test_multiple_events_news_generation()
        elif choice == "3":
            test_simulation_with_news_generation()
        elif choice == "4":
            test_news_generation_for_existing_events()
            test_multiple_events_news_generation()
            test_simulation_with_news_generation()
        else:
            print("❌ 잘못된 선택입니다.")
            return
            
    except KeyboardInterrupt:
        print("\n\n⏹️  테스트가 중단되었습니다.")
    
    print("\n✅ 뉴스 기사 생성 기능 테스트 완료!")


if __name__ == "__main__":
    main()
