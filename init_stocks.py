#!/usr/bin/env python3
"""
초기 주식 데이터 생성 스크립트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from sams.services import StockService

def main():
    """메인 함수"""
    print("🚀 SAMS 초기 주식 데이터 생성 시작")
    print("=" * 50)
    
    try:
        # 초기 주식 데이터 생성
        success = StockService.initialize_stocks()
        
        if success:
            print("✅ 초기 주식 데이터 생성 완료!")
            
            # 생성된 주식 목록 확인
            stocks = StockService.get_all_stocks()
            print(f"\n📊 생성된 주식 수: {len(stocks)}")
            
            print("\n📋 주식 목록:")
            for stock in stocks:
                print(f"   {stock['ticker']}: {stock['name']} - ₩{stock['current_price']:,}")
                
        else:
            print("❌ 주식 데이터 생성 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    print("\n🎯 다음 단계:")
    print("   1. Django 서버 실행: python3 manage.py runserver")
    print("   2. 브라우저에서 http://localhost:8000/portfolio/ 접속")
    print("   3. 포트폴리오 시스템 테스트")
    
    return True

if __name__ == "__main__":
    main() 