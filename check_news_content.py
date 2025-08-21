#!/usr/bin/env python3
"""
파이어스토어에서 뉴스 기사 내용을 조회하는 스크립트
"""

import sys
import os
from pathlib import Path
import environ

# 환경 변수 로드
environ.Env.read_env(str(Path(__file__).resolve().parent / ".env"))

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import list_event_logs, get_news_articles_for_event


def check_all_news_articles(sim_id: str = "default-sim"):
    """특정 시뮬레이션의 모든 뉴스 기사를 조회"""
    print(f"🔍 시뮬레이션 '{sim_id}'의 모든 뉴스 기사 조회")
    print("=" * 80)
    
    # 1. 이벤트 로그 조회
    event_logs = list_event_logs(sim_id, limit=20)
    
    if not event_logs:
        print("❌ 이벤트 로그를 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(event_logs)}개의 이벤트를 찾았습니다.")
    
    total_news_count = 0
    
    # 2. 각 이벤트별로 뉴스 기사 조회
    for i, event_log in enumerate(event_logs, 1):
        event = event_log.get("event", {})
        event_id = event.get("id", "unknown")
        event_type = event.get("event_type", "unknown")
        
        print(f"\n📰 이벤트 {i}: {event_type} (ID: {event_id})")
        print("-" * 60)
        
        # 해당 이벤트의 뉴스 기사들 조회
        news_articles = get_news_articles_for_event(sim_id, event_id)
        
        if news_articles:
            print(f"   📰 뉴스 기사 {len(news_articles)}개:")
            for j, news in enumerate(news_articles, 1):
                print(f"\n   {j}. {news.get('media_name', 'N/A')}")
                print(f"      생성시간: {news.get('created_at', 'N/A')}")
                print(f"      내용: {news.get('article_text', 'N/A')}")
                print(f"      언론사 성향: {news.get('meta', {}).get('outlet_bias', 'N/A')}")
                print(f"      신뢰도: {news.get('meta', {}).get('outlet_credibility', 'N/A')}")
                print("      " + "-" * 40)
            total_news_count += len(news_articles)
        else:
            print("   ❌ 뉴스 기사가 없습니다.")
    
    print(f"\n📊 총 {total_news_count}개의 뉴스 기사가 생성되었습니다.")


def check_specific_event_news(sim_id: str, event_id: str):
    """특정 이벤트의 뉴스 기사만 조회"""
    print(f"🔍 이벤트 '{event_id}'의 뉴스 기사 조회")
    print("=" * 80)
    
    news_articles = get_news_articles_for_event(sim_id, event_id)
    
    if not news_articles:
        print("❌ 뉴스 기사를 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(news_articles)}개의 뉴스 기사를 찾았습니다.")
    
    for i, news in enumerate(news_articles, 1):
        print(f"\n📰 뉴스 {i}: {news.get('media_name', 'N/A')}")
        print(f"   생성시간: {news.get('created_at', 'N/A')}")
        print(f"   언론사 성향: {news.get('meta', {}).get('outlet_bias', 'N/A')}")
        print(f"   신뢰도: {news.get('meta', {}).get('outlet_credibility', 'N/A')}")
        print(f"   내용:")
        print(f"   {news.get('article_text', 'N/A')}")
        print("-" * 60)


def check_news_by_media(sim_id: str, media_name: str):
    """특정 언론사의 뉴스 기사만 조회"""
    print(f"🔍 언론사 '{media_name}'의 뉴스 기사 조회")
    print("=" * 80)
    
    # 모든 이벤트의 뉴스 기사를 조회하여 필터링
    event_logs = list_event_logs(sim_id, limit=50)
    
    if not event_logs:
        print("❌ 이벤트 로그를 찾을 수 없습니다.")
        return
    
    matching_news = []
    
    for event_log in event_logs:
        event = event_log.get("event", {})
        event_id = event.get("id", "unknown")
        event_type = event.get("event_type", "unknown")
        
        news_articles = get_news_articles_for_event(sim_id, event_id)
        
        for news in news_articles:
            if news.get('media_name') == media_name:
                news['event_type'] = event_type
                news['event_id'] = event_id
                matching_news.append(news)
    
    if not matching_news:
        print(f"❌ '{media_name}'의 뉴스 기사를 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(matching_news)}개의 뉴스 기사를 찾았습니다.")
    
    for i, news in enumerate(matching_news, 1):
        print(f"\n📰 뉴스 {i}: {news.get('event_type', 'N/A')}")
        print(f"   이벤트 ID: {news.get('event_id', 'N/A')}")
        print(f"   생성시간: {news.get('created_at', 'N/A')}")
        print(f"   내용:")
        print(f"   {news.get('article_text', 'N/A')}")
        print("-" * 60)


def main():
    """메인 함수"""
    print("🎯 뉴스 기사 내용 확인 도구")
    print("=" * 60)
    
    # 시뮬레이션 ID 입력
    sim_id = input("시뮬레이션 ID를 입력하세요 (기본값: default-sim): ").strip()
    if not sim_id:
        sim_id = "default-sim"
    
    print(f"\n시뮬레이션 ID: {sim_id}")
    
    # 옵션 선택
    print("\n확인할 옵션을 선택하세요:")
    print("1. 모든 뉴스 기사 조회")
    print("2. 특정 이벤트의 뉴스 기사 조회")
    print("3. 특정 언론사의 뉴스 기사 조회")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            check_all_news_articles(sim_id)
        elif choice == "2":
            event_id = input("이벤트 ID를 입력하세요: ").strip()
            if event_id:
                check_specific_event_news(sim_id, event_id)
            else:
                print("❌ 이벤트 ID를 입력해주세요.")
        elif choice == "3":
            media_name = input("언론사 이름을 입력하세요 (예: 조선일보): ").strip()
            if media_name:
                check_news_by_media(sim_id, media_name)
            else:
                print("❌ 언론사 이름을 입력해주세요.")
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  조회가 중단되었습니다.")
    
    print("\n✅ 뉴스 기사 조회 완료!")


if __name__ == "__main__":
    main()
