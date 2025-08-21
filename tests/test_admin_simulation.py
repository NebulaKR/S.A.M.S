#!/usr/bin/env python3
"""
관리자 시뮬레이션 기능 테스트 스크립트
"""

import os
import sys
import time
import threading
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from sams.services import SimulationService

def test_simulation_service():
    """시뮬레이션 서비스 테스트"""
    print("=== 시뮬레이션 서비스 테스트 시작 ===")
    
    # 테스트 시뮬레이션 ID
    test_sim_id = "test-simulation-001"
    
    # 1. 시뮬레이션 시작 테스트
    print("\n1. 시뮬레이션 시작 테스트")
    settings = {
        'event_generation_interval': 10,  # 10초마다 이벤트 생성
        'news_generation_enabled': True,
        'max_events_per_hour': 5,
        'simulation_speed': 2,
        'allowed_categories': ['경제', '기업', '기술']
    }
    
    result = SimulationService.start_simulation(test_sim_id, settings)
    print(f"시뮬레이션 시작 결과: {result}")
    
    if result['success']:
        print("✅ 시뮬레이션이 성공적으로 시작되었습니다.")
        
        # 2. 상태 조회 테스트
        print("\n2. 상태 조회 테스트")
        for i in range(3):
            time.sleep(2)
            status = SimulationService.get_simulation_status(test_sim_id)
            if status:
                print(f"상태 조회 {i+1}: {status['status']} - 이벤트: {status['total_events']}, 뉴스: {status['total_news']}")
            else:
                print(f"상태 조회 {i+1}: 시뮬레이션을 찾을 수 없습니다.")
        
        # 3. 시뮬레이션 정지 테스트
        print("\n3. 시뮬레이션 정지 테스트")
        stop_result = SimulationService.stop_simulation(test_sim_id)
        print(f"시뮬레이션 정지 결과: {stop_result}")
        
        if stop_result['success']:
            print("✅ 시뮬레이션이 성공적으로 정지되었습니다.")
            
            # 4. 정지 후 상태 확인
            print("\n4. 정지 후 상태 확인")
            final_status = SimulationService.get_simulation_status(test_sim_id)
            if final_status:
                print(f"최종 상태: {final_status['status']}")
                print(f"총 생성된 이벤트: {final_status['total_events']}")
                print(f"총 생성된 뉴스: {final_status['total_news']}")
            else:
                print("시뮬레이션이 완전히 종료되었습니다.")
        else:
            print("❌ 시뮬레이션 정지에 실패했습니다.")
    else:
        print("❌ 시뮬레이션 시작에 실패했습니다.")
    
    # 5. 모든 시뮬레이션 상태 조회
    print("\n5. 모든 시뮬레이션 상태 조회")
    all_status = SimulationService.get_all_simulation_status()
    print(f"활성 시뮬레이션 수: {len(all_status)}")
    for sim_id, status in all_status.items():
        print(f"  - {sim_id}: {status['status']}")

def test_multiple_simulations():
    """여러 시뮬레이션 동시 실행 테스트"""
    print("\n=== 다중 시뮬레이션 테스트 시작 ===")
    
    sim_ids = ["multi-test-1", "multi-test-2", "multi-test-3"]
    
    # 여러 시뮬레이션 동시 시작
    print("여러 시뮬레이션을 동시에 시작합니다...")
    for i, sim_id in enumerate(sim_ids):
        settings = {
            'event_generation_interval': 15 + i * 5,  # 각각 다른 간격
            'news_generation_enabled': True,
            'max_events_per_hour': 3 + i,
            'simulation_speed': 1 + i,
            'allowed_categories': ['경제', '기업'] if i % 2 == 0 else ['기술', '국제']
        }
        
        result = SimulationService.start_simulation(sim_id, settings)
        print(f"시뮬레이션 {sim_id} 시작: {result['success']}")
    
    # 잠시 대기 후 상태 확인
    print("\n5초 후 상태 확인...")
    time.sleep(5)
    
    all_status = SimulationService.get_all_simulation_status()
    print(f"활성 시뮬레이션 수: {len(all_status)}")
    for sim_id, status in all_status.items():
        print(f"  - {sim_id}: {status['status']} (이벤트: {status['total_events']})")
    
    # 모든 시뮬레이션 정지
    print("\n모든 시뮬레이션을 정지합니다...")
    for sim_id in sim_ids:
        result = SimulationService.stop_simulation(sim_id)
        print(f"시뮬레이션 {sim_id} 정지: {result['success']}")

def test_error_handling():
    """에러 처리 테스트"""
    print("\n=== 에러 처리 테스트 시작 ===")
    
    # 1. 존재하지 않는 시뮬레이션 정지 시도
    print("1. 존재하지 않는 시뮬레이션 정지 시도")
    result = SimulationService.stop_simulation("non-existent-sim")
    print(f"결과: {result}")
    
    # 2. 존재하지 않는 시뮬레이션 상태 조회
    print("\n2. 존재하지 않는 시뮬레이션 상태 조회")
    status = SimulationService.get_simulation_status("non-existent-sim")
    print(f"상태: {status}")
    
    # 3. 이미 실행 중인 시뮬레이션 재시작 시도
    print("\n3. 이미 실행 중인 시뮬레이션 재시작 시도")
    test_sim_id = "duplicate-test"
    
    # 첫 번째 시작
    result1 = SimulationService.start_simulation(test_sim_id)
    print(f"첫 번째 시작: {result1['success']}")
    
    # 두 번째 시작 (중복)
    result2 = SimulationService.start_simulation(test_sim_id)
    print(f"두 번째 시작: {result2['success']} - {result2['message']}")
    
    # 정리
    SimulationService.stop_simulation(test_sim_id)

def main():
    """메인 테스트 함수"""
    print("관리자 시뮬레이션 기능 테스트")
    print("=" * 50)
    
    try:
        # 기본 시뮬레이션 서비스 테스트
        test_simulation_service()
        
        # 다중 시뮬레이션 테스트
        test_multiple_simulations()
        
        # 에러 처리 테스트
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

