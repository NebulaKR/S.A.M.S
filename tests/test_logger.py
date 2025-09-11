#!/usr/bin/env python3
"""
테스트용 로거 시스템
Firebase API 호출을 최소화하고 테스트 결과를 TSV 형식으로 저장
"""

import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class TestLogger:
    """테스트 결과를 TSV 형식으로 저장하는 로거"""
    
    def __init__(self, test_name: str, log_dir: str = "logs"):
        self.test_name = test_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # TSV 파일 경로
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tsv_file = self.log_dir / f"{test_name}_{timestamp}.tsv"
        self.json_file = self.log_dir / f"{test_name}_{timestamp}.json"
        
        # TSV 헤더
        self.tsv_headers = [
            'timestamp', 'test_step', 'operation', 'status', 
            'data_type', 'record_count', 'execution_time_ms', 
            'error_message', 'details'
        ]
        
        self._init_files()
    
    def _init_files(self):
        """TSV 파일 초기화"""
        with open(self.tsv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(self.tsv_headers)
    
    def log_operation(self, 
                     test_step: str,
                     operation: str,
                     status: str,
                     data_type: str = "",
                     record_count: int = 0,
                     execution_time_ms: float = 0.0,
                     error_message: str = "",
                     details: str = ""):
        """테스트 작업 로그 기록"""
        
        timestamp = datetime.now().isoformat()
        
        with open(self.tsv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow([
                timestamp, test_step, operation, status,
                data_type, record_count, execution_time_ms,
                error_message, details
            ])
    
    def log_data(self, data: Dict[str, Any], data_type: str = "test_data"):
        """테스트 데이터를 JSON으로 저장"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'test_name': self.test_name,
            'data_type': data_type,
            'data': data
        }
        
        # JSON 파일에 추가 (배열 형태)
        if self.json_file.exists():
            with open(self.json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.append(log_entry)
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    def log_summary(self, summary: Dict[str, Any]):
        """테스트 요약 정보 저장"""
        summary_file = self.log_dir / f"{self.test_name}_summary.json"
        
        summary_data = {
            'test_name': self.test_name,
            'timestamp': datetime.now().isoformat(),
            'summary': summary
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    def get_log_files(self) -> Dict[str, str]:
        """생성된 로그 파일들 반환"""
        return {
            'tsv_file': str(self.tsv_file),
            'json_file': str(self.json_file),
            'summary_file': str(self.log_dir / f"{self.test_name}_summary.json")
        }


class MockFirebaseData:
    """Firebase 데이터를 모킹하는 클래스"""
    
    def __init__(self):
        self.simulations = {}
        self.events = {}
        self.news = {}
        self.snapshots = {}
    
    def add_simulation(self, sim_id: str, data: Dict[str, Any]):
        """시뮬레이션 데이터 추가"""
        self.simulations[sim_id] = {
            'sim_id': sim_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **data
        }
    
    def add_event(self, sim_id: str, event_id: str, data: Dict[str, Any]):
        """이벤트 데이터 추가"""
        if sim_id not in self.events:
            self.events[sim_id] = {}
        
        self.events[sim_id][event_id] = {
            'event_id': event_id,
            'simulation_id': sim_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
    
    def add_news(self, sim_id: str, event_id: str, news_id: str, data: Dict[str, Any]):
        """뉴스 데이터 추가"""
        if sim_id not in self.news:
            self.news[sim_id] = {}
        if event_id not in self.news[sim_id]:
            self.news[sim_id][event_id] = {}
        
        self.news[sim_id][event_id][news_id] = {
            'news_id': news_id,
            'simulation_id': sim_id,
            'event_id': event_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
    
    def add_snapshot(self, sim_id: str, snapshot_id: str, data: Dict[str, Any]):
        """스냅샷 데이터 추가"""
        if sim_id not in self.snapshots:
            self.snapshots[sim_id] = {}
        
        self.snapshots[sim_id][snapshot_id] = {
            'snapshot_id': snapshot_id,
            'simulation_id': sim_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 생성"""
        total_events = sum(len(events) for events in self.events.values())
        total_news = sum(
            sum(len(news) for news in event_news.values()) 
            for event_news in self.news.values()
        )
        total_snapshots = sum(len(snapshots) for snapshots in self.snapshots.values())
        
        return {
            'total_simulations': len(self.simulations),
            'total_events': total_events,
            'total_news': total_news,
            'total_snapshots': total_snapshots,
            'simulation_details': [
                {
                    'simulation_id': sim_id,
                    'events_count': len(self.events.get(sim_id, {})),
                    'news_count': sum(
                        len(self.news.get(sim_id, {}).get(event_id, {}))
                        for event_id in self.events.get(sim_id, {})
                    ),
                    'snapshots_count': len(self.snapshots.get(sim_id, {})),
                    'last_activity': sim_data.get('updated_at')
                }
                for sim_id, sim_data in self.simulations.items()
            ]
        }
    
    def generate_test_data(self, num_simulations: int = 3, events_per_sim: int = 5):
        """테스트 데이터 생성"""
        print(f"🧪 {num_simulations}개 시뮬레이션에 대한 테스트 데이터 생성 중...")
        
        for i in range(num_simulations):
            sim_id = f"test-sim-{i+1}"
            
            # 시뮬레이션 데이터
            self.add_simulation(sim_id, {
                'name': f'테스트 시뮬레이션 {i+1}',
                'status': 'running' if i < 2 else 'stopped'
            })
            
            # 이벤트 데이터
            for j in range(events_per_sim):
                event_id = f"event-{i+1}-{j+1}"
                self.add_event(sim_id, event_id, {
                    'event_type': f'테스트 이벤트 {j+1}',
                    'category': ['경제', '정책', '기업', '기술', '국제'][j % 5],
                    'sentiment': round((j - 2) * 0.3, 2),
                    'impact_level': (j % 5) + 1,
                    'affected_stocks': [f'005930', f'005380', f'005490'][:j+1],
                    'market_impact': round((j - 2) * 0.1, 3)
                })
                
                # 뉴스 데이터 (각 이벤트당 2-3개)
                for k in range(2 + (j % 2)):
                    news_id = f"news-{i+1}-{j+1}-{k+1}"
                    self.add_news(sim_id, event_id, news_id, {
                        'media_name': ['조선일보', '중앙일보', '한국경제', '매일경제'][k % 4],
                        'article_text': f'테스트 뉴스 기사 {j+1}-{k+1}: {event_id}에 대한 보도',
                        'outlet_bias': round((k - 1) * 0.2, 2),
                        'outlet_credibility': round(0.6 + (k * 0.1), 2)
                    })
            
            # 스냅샷 데이터
            for j in range(events_per_sim):
                snapshot_id = f"snapshot-{i+1}-{j+1}"
                self.add_snapshot(sim_id, snapshot_id, {
                    'stocks': {
                        '005930': {'price': 75000 + (j * 1000), 'change': j * 0.5},
                        '005380': {'price': 45000 + (j * 500), 'change': j * 0.3},
                        '005490': {'price': 85000 + (j * 800), 'change': j * 0.4}
                    },
                    'market_params': {
                        'government': {'policy_direction': 0.2, 'interest_rate': 3.0},
                        'company': {'trait': 0.4, 'rnd_ratio': 0.3},
                        'public': {'risk_appetite': 0.3, 'news_sensitivity': 0.7}
                    }
                })
        
        print(f"✅ 테스트 데이터 생성 완료!")
        return self.get_statistics()


def run_database_test():
    """데이터베이스 관련 테스트 실행"""
    print("🧪 데이터베이스 테스트 시작")
    print("=" * 60)
    
    # 테스트 로거 초기화
    logger = TestLogger("database_test")
    
    # 모킹 데이터 생성
    mock_data = MockFirebaseData()
    stats = mock_data.generate_test_data(num_simulations=3, events_per_sim=5)
    
    # 통계 로깅
    logger.log_operation(
        test_step="data_generation",
        operation="generate_test_data",
        status="success",
        data_type="simulation_data",
        record_count=stats['total_simulations'],
        execution_time_ms=0.0,
        details=f"Generated {stats['total_simulations']} simulations"
    )
    
    # 상세 데이터 로깅
    logger.log_data(stats, "statistics")
    
    # 시뮬레이션별 상세 정보 로깅
    for sim_detail in stats['simulation_details']:
        logger.log_operation(
            test_step="simulation_analysis",
            operation="analyze_simulation",
            status="success",
            data_type="simulation_detail",
            record_count=1,
            execution_time_ms=0.0,
            details=f"Simulation {sim_detail['simulation_id']}: {sim_detail['events_count']} events, {sim_detail['news_count']} news"
        )
    
    # 요약 정보 저장
    summary = {
        'total_simulations': stats['total_simulations'],
        'total_events': stats['total_events'],
        'total_news': stats['total_news'],
        'total_snapshots': stats['total_snapshots'],
        'test_duration': '0.0s',
        'status': 'completed'
    }
    
    logger.log_summary(summary)
    
    # 로그 파일 정보 출력
    log_files = logger.get_log_files()
    print(f"\n📊 테스트 결과 파일:")
    print(f"  - TSV 로그: {log_files['tsv_file']}")
    print(f"  - JSON 데이터: {log_files['json_file']}")
    print(f"  - 요약 정보: {log_files['summary_file']}")
    
    print(f"\n📈 생성된 데이터:")
    print(f"  - 시뮬레이션: {stats['total_simulations']}개")
    print(f"  - 이벤트: {stats['total_events']}개")
    print(f"  - 뉴스: {stats['total_news']}개")
    print(f"  - 스냅샷: {stats['total_snapshots']}개")
    
    return log_files


if __name__ == "__main__":
    run_database_test()
