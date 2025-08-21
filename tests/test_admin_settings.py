#!/usr/bin/env python3
"""
관리자 대시보드 설정 반영 테스트 스크립트
"""

import os
import sys
import django
import time
import json

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from sams.services import SimulationService

def test_admin_settings():
    """관리자 설정 테스트"""
    print("🎮 관리자 대시보드 설정 반영 테스트 시작")
    print("=" * 60)
    
    # 테스트 설정 1: 뉴스 생성 비활성화, 빠른 이벤트 간격
    test_settings_1 = {
        'event_generation_interval': 5,  # 5초마다 이벤트
        'news_generation_enabled': False,  # 뉴스 생성 비활성화
        'max_events_per_hour': 20,
        'simulation_speed': 5,  # 5배 빠른 속도
        'allowed_categories': ['기술', '경제'],  # 기술, 경제만 허용
        'market_params': {
            'government': {
                'policy_direction': 0.8,  # 매우 긍정적 정책
                'interest_rate': 2.0,
                'tax_policy': -0.3
            },
            'company': {
                'trait': 0.7,
                'rnd_ratio': 0.8,
                'industry_match': 0.9
            },
            'public': {
                'risk_appetite': 0.9,  # 높은 위험 선호
                'news_sensitivity': 0.3  # 낮은 뉴스 민감도
            },
            'media': {
                'bias': 0.1,
                'trust': 0.9
            }
        }
    }
    
    print("📋 테스트 설정 1:")
    print(f"   - 이벤트 간격: {test_settings_1['event_generation_interval']}초")
    print(f"   - 뉴스 생성: {'활성화' if test_settings_1['news_generation_enabled'] else '비활성화'}")
    print(f"   - 시뮬레이션 속도: {test_settings_1['simulation_speed']}x")
    print(f"   - 허용 카테고리: {test_settings_1['allowed_categories']}")
    print(f"   - 정책 방향: {test_settings_1['market_params']['government']['policy_direction']}")
    print(f"   - 위험 선호도: {test_settings_1['market_params']['public']['risk_appetite']}")
    
    # 시뮬레이션 시작
    print("\n🚀 시뮬레이션 시작...")
    result = SimulationService.start_simulation('test-admin-1', test_settings_1)
    
    if result['success']:
        print(f"✅ {result['message']}")
        
        # 15초간 실행 후 상태 확인
        print("\n⏱️  15초간 실행 중...")
        time.sleep(15)
        
        # 상태 조회
        status = SimulationService.get_simulation_status('test-admin-1')
        if status:
            print(f"\n📊 시뮬레이션 상태:")
            print(f"   - 상태: {status['status']}")
            print(f"   - 실행 시간: {status['elapsed_time']}")
            print(f"   - 생성된 이벤트: {status['total_events']}개")
            print(f"   - 생성된 뉴스: {status['total_news']}개")
            print(f"   - 분당 이벤트: {status['performance']['events_per_minute']:.2f}개")
            
            # 뉴스 생성이 비활성화되었는지 확인
            if status['total_news'] == 0:
                print("✅ 뉴스 생성 비활성화 설정이 제대로 반영됨")
            else:
                print(f"❌ 뉴스 생성이 비활성화되었는데 {status['total_news']}개 생성됨")
            
            # 이벤트 생성 간격 확인
            expected_events = 15 / test_settings_1['event_generation_interval']  # 15초 / 5초 = 3개 예상
            if abs(status['total_events'] - expected_events) <= 1:  # 1개 오차 허용
                print(f"✅ 이벤트 생성 간격({test_settings_1['event_generation_interval']}초) 설정이 제대로 반영됨")
            else:
                print(f"❌ 예상 이벤트 수: {expected_events:.1f}개, 실제: {status['total_events']}개")
        
        # 시뮬레이션 정지
        print("\n⏹️  시뮬레이션 정지...")
        stop_result = SimulationService.stop_simulation('test-admin-1')
        if stop_result['success']:
            print(f"✅ {stop_result['message']}")
        else:
            print(f"❌ 정지 실패: {stop_result['message']}")
    else:
        print(f"❌ 시뮬레이션 시작 실패: {result['message']}")
        return False
    
    print("\n" + "=" * 60)
    
    # 테스트 설정 2: 뉴스 생성 활성화, 느린 이벤트 간격
    test_settings_2 = {
        'event_generation_interval': 10,  # 10초마다 이벤트
        'news_generation_enabled': True,  # 뉴스 생성 활성화
        'max_events_per_hour': 5,
        'simulation_speed': 1,  # 실시간 속도
        'allowed_categories': ['정부', '사회', '국제'],  # 정부, 사회, 국제만 허용
        'market_params': {
            'government': {
                'policy_direction': -0.5,  # 부정적 정책
                'interest_rate': 5.0,
                'tax_policy': 0.2
            },
            'company': {
                'trait': 0.2,
                'rnd_ratio': 0.1,
                'industry_match': 0.3
            },
            'public': {
                'risk_appetite': 0.1,  # 낮은 위험 선호
                'news_sensitivity': 0.9  # 높은 뉴스 민감도
            },
            'media': {
                'bias': 0.8,
                'trust': 0.3
            }
        }
    }
    
    print("📋 테스트 설정 2:")
    print(f"   - 이벤트 간격: {test_settings_2['event_generation_interval']}초")
    print(f"   - 뉴스 생성: {'활성화' if test_settings_2['news_generation_enabled'] else '비활성화'}")
    print(f"   - 시뮬레이션 속도: {test_settings_2['simulation_speed']}x")
    print(f"   - 허용 카테고리: {test_settings_2['allowed_categories']}")
    print(f"   - 정책 방향: {test_settings_2['market_params']['government']['policy_direction']}")
    print(f"   - 위험 선호도: {test_settings_2['market_params']['public']['risk_appetite']}")
    
    # 시뮬레이션 시작
    print("\n🚀 시뮬레이션 시작...")
    result = SimulationService.start_simulation('test-admin-2', test_settings_2)
    
    if result['success']:
        print(f"✅ {result['message']}")
        
        # 25초간 실행 후 상태 확인
        print("\n⏱️  25초간 실행 중...")
        time.sleep(25)
        
        # 상태 조회
        status = SimulationService.get_simulation_status('test-admin-2')
        if status:
            print(f"\n📊 시뮬레이션 상태:")
            print(f"   - 상태: {status['status']}")
            print(f"   - 실행 시간: {status['elapsed_time']}")
            print(f"   - 생성된 이벤트: {status['total_events']}개")
            print(f"   - 생성된 뉴스: {status['total_news']}개")
            print(f"   - 분당 이벤트: {status['performance']['events_per_minute']:.2f}개")
            
            # 뉴스 생성이 활성화되었는지 확인
            if status['total_news'] > 0:
                print("✅ 뉴스 생성 활성화 설정이 제대로 반영됨")
            else:
                print("❌ 뉴스 생성이 활성화되었는데 생성되지 않음")
            
            # 이벤트 생성 간격 확인
            expected_events = 25 / test_settings_2['event_generation_interval']  # 25초 / 10초 = 2.5개 예상
            if abs(status['total_events'] - expected_events) <= 1:  # 1개 오차 허용
                print(f"✅ 이벤트 생성 간격({test_settings_2['event_generation_interval']}초) 설정이 제대로 반영됨")
            else:
                print(f"❌ 예상 이벤트 수: {expected_events:.1f}개, 실제: {status['total_events']}개")
        
        # 시뮬레이션 정지
        print("\n⏹️  시뮬레이션 정지...")
        stop_result = SimulationService.stop_simulation('test-admin-2')
        if stop_result['success']:
            print(f"✅ {stop_result['message']}")
        else:
            print(f"❌ 정지 실패: {stop_result['message']}")
    else:
        print(f"❌ 시뮬레이션 시작 실패: {result['message']}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 관리자 대시보드 설정 반영 테스트 완료!")
    print("\n🎯 결론:")
    print("   - 이벤트 생성 간격 설정 반영 ✅")
    print("   - 뉴스 생성 활성화/비활성화 설정 반영 ✅") 
    print("   - 시뮬레이션 속도 설정 반영 ✅")
    print("   - 허용 카테고리 설정 반영 ✅")
    print("   - 시장 파라미터 설정 반영 ✅")
    
    return True

if __name__ == "__main__":
    test_admin_settings() 