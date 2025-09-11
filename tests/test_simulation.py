#!/usr/bin/env python3
"""
SAMS 시뮬레이션 엔진 테스트 스크립트
"""
from pathlib import Path
import environ
environ.Env.read_env(str(Path(__file__).resolve().parent / ".env"))

import time
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.models.simulation_engine import SimulationEngine, SimulationSpeed


def on_price_change(stock_price):
    """주가 변화 콜백"""
    print(f"📈 {stock_price.ticker}: ₩{stock_price.current_price:,.0f} "
          f"({stock_price.change_rate:+.2%})")


def on_event_occur(sim_event):
    """이벤트 발생 콜백"""
    print(f"📰 이벤트: {sim_event.event.event_type}")
    print(f"   카테고리: {sim_event.event.category}")
    print(f"   영향도: {sim_event.market_impact:.3f}")
    print(f"   영향받는 종목: {', '.join(sim_event.affected_stocks)}")
    print()


def main():
    """메인 테스트 함수"""
    print("🚀 SAMS 시뮬레이션 엔진 테스트 시작")
    print("=" * 50)
    
    # 초기 시장 데이터 설정
    initial_data = {
        "stocks": {
            "005930": {"price": 79000, "volume": 1000000, "base_price": 79000},  # 삼성전자
            "000660": {"price": 45000, "volume": 500000, "base_price": 45000},   # SK하이닉스
            "005380": {"price": 180000, "volume": 300000, "base_price": 180000}, # 현대차
            "005490": {"price": 85000, "volume": 400000, "base_price": 85000},   # 기아
            "035420": {"price": 220000, "volume": 200000, "base_price": 220000}, # NAVER
            "051910": {"price": 520000, "volume": 150000, "base_price": 520000}, # LG화학
            "006400": {"price": 380000, "volume": 180000, "base_price": 380000}, # 삼성SDI
            "012450": {"price": 45000, "volume": 250000, "base_price": 45000},  # 한화에어로스페이스
            "055550": {"price": 45000, "volume": 300000, "base_price": 45000},  # 신한지주
            "086790": {"price": 42000, "volume": 280000, "base_price": 42000},  # 하나금융지주
            "105560": {"price": 65000, "volume": 220000, "base_price": 65000},  # KB금융
            "138930": {"price": 8500, "volume": 500000, "base_price": 8500},   # BNK금융지주
            "028260": {"price": 45000, "volume": 200000, "base_price": 45000},  # 삼성물산
            "009540": {"price": 120000, "volume": 180000, "base_price": 120000}, # 현대중공업
            "010140": {"price": 8500, "volume": 400000, "base_price": 8500},   # 삼성중공업
            "017670": {"price": 52000, "volume": 250000, "base_price": 52000},  # SK텔레콤
            "030200": {"price": 35000, "volume": 300000, "base_price": 35000},  # KT
            "011070": {"price": 180000, "volume": 150000, "base_price": 180000}, # LG이노텍
            "015760": {"price": 22000, "volume": 800000, "base_price": 22000},  # 한국전력
            "096770": {"price": 120000, "volume": 200000, "base_price": 120000}, # SK이노베이션
            "068270": {"price": 180000, "volume": 120000, "base_price": 180000}, # 셀트리온
            "207940": {"price": 850000, "volume": 80000, "base_price": 850000},  # 삼성바이오로직스
            "097950": {"price": 380000, "volume": 100000, "base_price": 380000}, # CJ제일제당
            "035720": {"price": 45000, "volume": 350000, "base_price": 45000},  # 카카오
            "323410": {"price": 28000, "volume": 400000, "base_price": 28000},  # 카카오뱅크
            "373220": {"price": 450000, "volume": 120000, "base_price": 450000}, # LG에너지솔루션
        },
        "market_params": {
            "public": {"risk_appetite": 0.3, "news_sensitivity": 0.7},
            "government": {"policy_direction": 0.2},
            "company": {"orientation": 0.1, "rnd_focus": 0.4}
        }
    }
    
    # 시뮬레이션 엔진 초기화
    engine = SimulationEngine(initial_data)
    
    # 콜백 함수 등록
    engine.add_callback("price_change", on_price_change)
    engine.add_callback("event_occur", on_event_occur)
    
    # 시뮬레이션 시작
    print("시뮬레이션 시작...")
    engine.start()
    
    try:
        # 시뮬레이션 루프
        for i in range(30):  # 30초 동안 실행
            engine.update()
            
            # 5초마다 현재 상태 출력
            if i % 5 == 0:
                state = engine.get_current_state()
                print(f"\n⏰ 시뮬레이션 시간: {state['simulation_time']}")
                print(f"📊 현재 주가:")
                for ticker, data in state['stocks'].items():
                    price = data['price']
                    change_rate = data.get('change_rate', 0.0)
                    print(f"   {ticker}: ₩{price:,.0f} ({change_rate:+.2%})")
                print("-" * 30)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단됨")
    
    # 시뮬레이션 정지
    engine.stop()
    
    # 최종 결과 출력
    print("\n📋 시뮬레이션 결과 요약")
    print("=" * 50)
    
    final_state = engine.get_current_state()
    print(f"총 실행 시간: {final_state['simulation_time']}")
    print(f"발생한 이벤트 수: {len(final_state['recent_events'])}")
    
    print("\n📈 최종 주가:")
    for ticker, data in final_state['stocks'].items():
        initial_price = initial_data['stocks'][ticker]['price']
        final_price = data['price']
        total_change = (final_price - initial_price) / initial_price
        print(f"   {ticker}: ₩{final_price:,.0f} (전체 변화: {total_change:+.2%})")
    
    print("\n✅ 시뮬레이션 테스트 완료!")


if __name__ == "__main__":
    main() 