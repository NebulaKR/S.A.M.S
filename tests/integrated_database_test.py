#!/usr/bin/env python3
"""
통합 데이터베이스 테스트
Firebase API 호출 없이 모든 데이터베이스 관련 기능을 테스트
"""

import sys
import os
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from test_logger import TestLogger
from mock_firebase import MockFirebaseSystem
from test_data_generator import TestDataGenerator

class IntegratedDatabaseTest:
    """통합 데이터베이스 테스트 클래스"""
    
    def __init__(self):
        self.logger = TestLogger("integrated_database_test")
        self.mock_firebase = MockFirebaseSystem()
        self.data_generator = TestDataGenerator()
        self.test_results = {}
    
    def test_data_generation(self):
        """테스트 데이터 생성 테스트"""
        print("🧪 1. 테스트 데이터 생성 테스트")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 테스트 데이터 생성
            data = self.data_generator.generate_all_test_data(num_simulations=3)
            
            execution_time = (time.time() - start_time) * 1000
            
            # 로그 기록
            self.logger.log_operation(
                test_step="data_generation",
                operation="generate_test_data",
                status="success",
                data_type="simulation_data",
                record_count=data['statistics']['total_simulations'],
                execution_time_ms=execution_time,
                details=f"Generated {data['statistics']['total_simulations']} simulations"
            )
            
            # 데이터 저장
            self.logger.log_data(data['statistics'], "generated_statistics")
            
            self.test_results['data_generation'] = {
                'status': 'success',
                'execution_time_ms': execution_time,
                'records_generated': data['statistics']['total_simulations']
            }
            
            print(f"✅ 데이터 생성 성공: {execution_time:.2f}ms")
            print(f"   - 시뮬레이션: {data['statistics']['total_simulations']}개")
            print(f"   - 이벤트: {data['statistics']['total_events']}개")
            print(f"   - 뉴스: {data['statistics']['total_news']}개")
            print(f"   - 스냅샷: {data['statistics']['total_snapshots']}개")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.log_operation(
                test_step="data_generation",
                operation="generate_test_data",
                status="error",
                data_type="simulation_data",
                record_count=0,
                execution_time_ms=execution_time,
                error_message=str(e),
                details="Data generation failed"
            )
            
            self.test_results['data_generation'] = {
                'status': 'error',
                'execution_time_ms': execution_time,
                'error': str(e)
            }
            
            print(f"❌ 데이터 생성 실패: {e}")
    
    def test_firebase_mocking(self):
        """Firebase 모킹 테스트"""
        print("\n🧪 2. Firebase 모킹 테스트")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 모킹 데이터 로드
            self.mock_firebase.load_test_data()
            
            # 통계 조회
            stats = self.mock_firebase.get_statistics()
            
            execution_time = (time.time() - start_time) * 1000
            
            # 로그 기록
            self.logger.log_operation(
                test_step="firebase_mocking",
                operation="get_statistics",
                status="success",
                data_type="firebase_statistics",
                record_count=stats['total_simulations'],
                execution_time_ms=execution_time,
                details=f"Retrieved statistics for {stats['total_simulations']} simulations"
            )
            
            # 상세 데이터 로깅
            self.logger.log_data(stats, "firebase_statistics")
            
            self.test_results['firebase_mocking'] = {
                'status': 'success',
                'execution_time_ms': execution_time,
                'simulations': stats['total_simulations'],
                'events': stats['total_events'],
                'news': stats['total_news'],
                'snapshots': stats['total_snapshots']
            }
            
            print(f"✅ Firebase 모킹 성공: {execution_time:.2f}ms")
            print(f"   - 시뮬레이션: {stats['total_simulations']}개")
            print(f"   - 이벤트: {stats['total_events']}개")
            print(f"   - 뉴스: {stats['total_news']}개")
            print(f"   - 스냅샷: {stats['total_snapshots']}개")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.log_operation(
                test_step="firebase_mocking",
                operation="get_statistics",
                status="error",
                data_type="firebase_statistics",
                record_count=0,
                execution_time_ms=execution_time,
                error_message=str(e),
                details="Firebase mocking failed"
            )
            
            self.test_results['firebase_mocking'] = {
                'status': 'error',
                'execution_time_ms': execution_time,
                'error': str(e)
            }
            
            print(f"❌ Firebase 모킹 실패: {e}")
    
    def test_data_export(self):
        """데이터 내보내기 테스트"""
        print("\n🧪 3. 데이터 내보내기 테스트")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 테스트 데이터 생성
            data = self.data_generator.generate_all_test_data(num_simulations=2)
            
            # TSV 파일로 저장
            tsv_files = self.data_generator.save_to_tsv(data, "export_test")
            
            # JSON 파일로 저장
            json_files = self.data_generator.save_to_json(data, "export_test")
            
            execution_time = (time.time() - start_time) * 1000
            
            # 로그 기록
            self.logger.log_operation(
                test_step="data_export",
                operation="export_to_files",
                status="success",
                data_type="export_data",
                record_count=len(tsv_files) + len(json_files),
                execution_time_ms=execution_time,
                details=f"Exported to {len(tsv_files)} TSV and {len(json_files)} JSON files"
            )
            
            # 파일 정보 로깅
            export_info = {
                'tsv_files': tsv_files,
                'json_files': json_files,
                'total_records': data['statistics']['total_simulations']
            }
            self.logger.log_data(export_info, "export_info")
            
            self.test_results['data_export'] = {
                'status': 'success',
                'execution_time_ms': execution_time,
                'tsv_files': len(tsv_files),
                'json_files': len(json_files),
                'files': {**tsv_files, **json_files}
            }
            
            print(f"✅ 데이터 내보내기 성공: {execution_time:.2f}ms")
            print(f"   - TSV 파일: {len(tsv_files)}개")
            print(f"   - JSON 파일: {len(json_files)}개")
            
            for file_type, filepath in {**tsv_files, **json_files}.items():
                print(f"     - {file_type}: {filepath}")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.log_operation(
                test_step="data_export",
                operation="export_to_files",
                status="error",
                data_type="export_data",
                record_count=0,
                execution_time_ms=execution_time,
                error_message=str(e),
                details="Data export failed"
            )
            
            self.test_results['data_export'] = {
                'status': 'error',
                'execution_time_ms': execution_time,
                'error': str(e)
            }
            
            print(f"❌ 데이터 내보내기 실패: {e}")
    
    def test_performance_benchmark(self):
        """성능 벤치마크 테스트"""
        print("\n🧪 4. 성능 벤치마크 테스트")
        print("-" * 40)
        
        # 다양한 데이터 크기로 테스트
        test_sizes = [1, 3, 5, 10]
        performance_results = {}
        
        for size in test_sizes:
            print(f"   테스트 크기: {size}개 시뮬레이션")
            
            start_time = time.time()
            
            try:
                # 데이터 생성
                data = self.data_generator.generate_all_test_data(num_simulations=size)
                
                # 모킹 시스템 테스트
                self.mock_firebase.load_test_data()
                stats = self.mock_firebase.get_statistics()
                
                execution_time = (time.time() - start_time) * 1000
                
                performance_results[size] = {
                    'simulations': size,
                    'events': data['statistics']['total_events'],
                    'news': data['statistics']['total_news'],
                    'snapshots': data['statistics']['total_snapshots'],
                    'execution_time_ms': execution_time,
                    'records_per_second': (data['statistics']['total_simulations'] + 
                                         data['statistics']['total_events'] + 
                                         data['statistics']['total_news'] + 
                                         data['statistics']['total_snapshots']) / (execution_time / 1000)
                }
                
                print(f"     ✅ 완료: {execution_time:.2f}ms")
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                performance_results[size] = {
                    'simulations': size,
                    'execution_time_ms': execution_time,
                    'error': str(e)
                }
                print(f"     ❌ 실패: {e}")
        
        # 성능 결과 로깅
        self.logger.log_data(performance_results, "performance_benchmark")
        
        self.test_results['performance_benchmark'] = performance_results
        
        print(f"\n📊 성능 벤치마크 결과:")
        for size, result in performance_results.items():
            if 'error' not in result:
                print(f"   {size}개 시뮬레이션: {result['execution_time_ms']:.2f}ms "
                      f"({result['records_per_second']:.1f} records/sec)")
            else:
                print(f"   {size}개 시뮬레이션: 실패 - {result['error']}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 통합 데이터베이스 테스트 시작")
        print("=" * 60)
        
        total_start_time = time.time()
        
        # 각 테스트 실행
        self.test_data_generation()
        self.test_firebase_mocking()
        self.test_data_export()
        self.test_performance_benchmark()
        
        total_execution_time = time.time() - total_start_time
        
        # 전체 요약 생성
        summary = {
            'total_execution_time_seconds': total_execution_time,
            'test_results': self.test_results,
            'overall_status': 'success' if all(
                result.get('status') == 'success' 
                for result in self.test_results.values() 
                if isinstance(result, dict) and 'status' in result
            ) else 'partial_success'
        }
        
        # 요약 로깅
        self.logger.log_summary(summary)
        
        # 로그 파일 정보 출력
        log_files = self.logger.get_log_files()
        
        print(f"\n🎯 테스트 완료!")
        print(f"   총 실행 시간: {total_execution_time:.2f}초")
        print(f"   전체 상태: {summary['overall_status']}")
        
        print(f"\n📁 생성된 로그 파일들:")
        for file_type, filepath in log_files.items():
            print(f"   - {file_type}: {filepath}")
        
        return summary


def main():
    """메인 함수"""
    test = IntegratedDatabaseTest()
    summary = test.run_all_tests()
    return summary


if __name__ == "__main__":
    main()
