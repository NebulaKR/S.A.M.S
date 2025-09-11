#!/usr/bin/env python3
"""
테스트 실행 스크립트
Firebase API 호출 없이 모든 데이터베이스 테스트를 실행
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def main():
    """메인 함수"""
    print("🚀 SAMS 데이터베이스 테스트 시스템")
    print("=" * 50)
    print("Firebase API 호출 없이 로컬에서 테스트를 실행합니다.")
    print()
    
    # 테스트 옵션 선택
    print("실행할 테스트를 선택하세요:")
    print("1. 통합 데이터베이스 테스트 (권장)")
    print("2. 데이터 생성기 테스트")
    print("3. Firebase 모킹 테스트")
    print("4. 로거 시스템 테스트")
    print("5. 모든 테스트 실행")
    
    try:
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == "1":
            print("\n🧪 통합 데이터베이스 테스트 실행 중...")
            from integrated_database_test import main as run_integrated_test
            run_integrated_test()
            
        elif choice == "2":
            print("\n🧪 데이터 생성기 테스트 실행 중...")
            from test_data_generator import run_data_generation_test
            run_data_generation_test()
            
        elif choice == "3":
            print("\n🧪 Firebase 모킹 테스트 실행 중...")
            from mock_firebase import main as run_mock_test
            run_mock_test()
            
        elif choice == "4":
            print("\n🧪 로거 시스템 테스트 실행 중...")
            from test_logger import run_database_test
            run_database_test()
            
        elif choice == "5":
            print("\n🧪 모든 테스트 실행 중...")
            
            # 통합 테스트
            print("\n1️⃣ 통합 데이터베이스 테스트")
            from integrated_database_test import main as run_integrated_test
            run_integrated_test()
            
            # 개별 테스트들
            print("\n2️⃣ 데이터 생성기 테스트")
            from test_data_generator import run_data_generation_test
            run_data_generation_test()
            
            print("\n3️⃣ Firebase 모킹 테스트")
            from mock_firebase import main as run_mock_test
            run_mock_test()
            
            print("\n4️⃣ 로거 시스템 테스트")
            from test_logger import run_database_test
            run_database_test()
            
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        print("\n✅ 테스트 완료!")
        print("\n📁 생성된 로그 파일들을 확인하세요:")
        print("   - logs/ 폴더에 TSV 및 JSON 파일들이 생성되었습니다.")
        print("   - TSV 파일: 테스트 실행 로그 (탭 구분)")
        print("   - JSON 파일: 상세 데이터 및 통계")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

