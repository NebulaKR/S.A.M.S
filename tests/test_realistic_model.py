#!/usr/bin/env python3
"""
현실적인 주가 변동 모델 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.models.realistic_stock_movement import RealisticStockMovement

def test_realistic_model():
    """현실적인 주가 변동 모델 테스트"""
    print("🚀 현실적인 주가 변동 모델 테스트 시작")
    print("=" * 60)
    
    # 모델 초기화
    model = RealisticStockMovement()
    
    # 테스트 이벤트들
    test_events = [
        {
            "event_type": "AI 기술 혁신",
            "category": "기술",
            "sentiment": 0.8,      # 매우 긍정적
            "impact_level": 4      # 높은 영향도
        },
        {
            "event_type": "정부 규제 강화",
            "category": "정부",
            "sentiment": -0.6,     # 부정적
            "impact_level": 3      # 중간 영향도
        },
        {
            "event_type": "경제 침체 우려",
            "category": "경제",
            "sentiment": -0.4,     # 약간 부정적
            "impact_level": 2      # 낮은 영향도
        },
        {
            "event_type": "바이오 신약 승인",
            "category": "기술",
            "sentiment": 0.9,      # 매우 긍정적
            "impact_level": 5      # 최고 영향도
        }
    ]
    
    # 테스트 주식들 (다양한 섹터)
    test_stocks = [
        ('005930', '삼성전자', 79000),      # IT/전자
        ('005380', '현대차', 45000),        # 자동차
        ('055550', '신한지주', 52000),      # 금융
        ('068270', '셀트리온', 180000),     # 바이오
        ('005490', '포스코홀딩스', 85000),  # 철강/소재
        ('097950', 'CJ대한통운', 42000)     # 물류/운송
    ]
    
    print("📊 테스트 결과:")
    print("-" * 60)
    
    for event in test_events:
        print(f"\n🎯 이벤트: {event['event_type']}")
        print(f"   카테고리: {event['category']}, 감정: {event['sentiment']:.1f}, 영향도: {event['impact_level']}")
        print("-" * 40)
        
        for ticker, name, base_price in test_stocks:
            result = model.calculate_realistic_change(
                event=event,
                stock_code=ticker,
                current_price=base_price
            )
            
            change_percent = result['delta'] * 100
            new_price = result['price']
            volume_change = result['volume']
            
            # 변화 방향에 따른 이모지
            if change_percent > 0:
                direction = "📈"
            elif change_percent < 0:
                direction = "📉"
            else:
                direction = "➡️"
            
            print(f"   {direction} {ticker} ({name}): {base_price:,.0f} → {new_price:,.0f} ({change_percent:+.2f}%) [거래량: {volume_change:.1f}x]")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    
    # 주식별 특성 요약 출력
    print("\n📋 주식별 특성 요약:")
    print("-" * 60)
    for ticker, name, _ in test_stocks:
        summary = model.get_stock_summary(ticker)
        if summary:
            print(f"   {ticker} ({name}):")
            print(f"     - 섹터: {summary['sector']}")
            print(f"     - 시장규모: {summary['market_cap']}")
            print(f"     - 변동성: {summary['volatility']:.2f}")
            print(f"     - 뉴스민감도: {summary['news_sensitivity']:.2f}")
            print(f"     - 과거변동성: {summary['historical_volatility']:.3f}")
            print()

if __name__ == "__main__":
    test_realistic_model() 