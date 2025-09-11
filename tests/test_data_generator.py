#!/usr/bin/env python3
"""
TSV 형식 테스트 데이터 생성기
Firebase API 호출 없이 테스트용 데이터를 생성하고 TSV/JSON 형식으로 저장
"""

import csv
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class TestDataGenerator:
    """테스트 데이터 생성기"""
    
    def __init__(self, output_dir: str = "logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 테스트 데이터 템플릿
        self.event_types = [
            "AI 기술 혁신", "정부 규제 강화", "경제 침체 우려", "바이오 신약 승인",
            "반도체 수요 증가", "친환경 정책 발표", "금리 인상", "주식 시장 급등",
            "기업 실적 발표", "국제 무역 갈등", "원자재 가격 상승", "디지털 전환 가속화"
        ]
        
        self.categories = ["경제", "정책", "기업", "기술", "국제", "사회", "환경"]
        
        self.media_outlets = [
            "조선일보", "중앙일보", "한국경제", "매일경제", "서울경제", 
            "이데일리", "아시아경제", "헤럴드경제", "뉴스1", "연합뉴스"
        ]
        
        self.stock_codes = [
            "005930", "005380", "005490", "051910", "097950", "000660", 
            "035420", "068270", "207940", "006400"
        ]
        
        self.stock_names = {
            "005930": "삼성전자", "005380": "현대차", "005490": "포스코홀딩스",
            "051910": "LG화학", "097950": "CJ대한통운", "000660": "SK하이닉스",
            "035420": "NAVER", "068270": "셀트리온", "207940": "삼성바이오로직스",
            "006400": "삼성SDI"
        }
    
    def generate_simulation_data(self, num_simulations: int = 5) -> List[Dict[str, Any]]:
        """시뮬레이션 데이터 생성"""
        simulations = []
        
        for i in range(num_simulations):
            sim_id = f"sim-{i+1:03d}"
            created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            simulation = {
                'simulation_id': sim_id,
                'name': f'시뮬레이션 {i+1}',
                'status': random.choice(['running', 'stopped', 'paused']),
                'created_at': created_at.isoformat(),
                'updated_at': (created_at + timedelta(hours=random.randint(1, 24))).isoformat(),
                'description': f'테스트용 시뮬레이션 {i+1}입니다.',
                'parameters': {
                    'event_interval': random.randint(30, 300),
                    'simulation_speed': random.choice([1, 2, 5, 10]),
                    'max_events_per_hour': random.randint(5, 20)
                }
            }
            simulations.append(simulation)
        
        return simulations
    
    def generate_event_data(self, simulation_id: str, num_events: int = 10) -> List[Dict[str, Any]]:
        """이벤트 데이터 생성"""
        events = []
        
        for i in range(num_events):
            event_id = f"event-{simulation_id}-{i+1:03d}"
            created_at = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            event_type = random.choice(self.event_types)
            category = random.choice(self.categories)
            sentiment = round(random.uniform(-1.0, 1.0), 2)
            impact_level = random.randint(1, 5)
            
            # 영향받는 주식 선택 (1-3개)
            affected_stocks = random.sample(self.stock_codes, random.randint(1, 3))
            
            event = {
                'event_id': event_id,
                'simulation_id': simulation_id,
                'event_type': event_type,
                'category': category,
                'sentiment': sentiment,
                'impact_level': impact_level,
                'affected_stocks': affected_stocks,
                'market_impact': round(sentiment * impact_level * 0.1, 3),
                'created_at': created_at.isoformat(),
                'description': f'{event_type}에 대한 상세 설명입니다.',
                'source': random.choice(['정부 발표', '기업 공시', '뉴스 보도', '분석가 리포트'])
            }
            events.append(event)
        
        return events
    
    def generate_news_data(self, simulation_id: str, event_id: str, num_news: int = 3) -> List[Dict[str, Any]]:
        """뉴스 데이터 생성"""
        news_list = []
        
        for i in range(num_news):
            news_id = f"news-{event_id}-{i+1:02d}"
            created_at = datetime.now() - timedelta(minutes=random.randint(5, 60))
            
            media_name = random.choice(self.media_outlets)
            outlet_bias = round(random.uniform(-0.5, 0.5), 2)
            outlet_credibility = round(random.uniform(0.3, 0.9), 2)
            
            # 뉴스 기사 텍스트 생성
            article_templates = [
                f"{media_name}는 {event_id}와 관련하여 다음과 같이 보도했습니다.",
                f"최근 {event_id}에 대한 {media_name}의 분석 결과를 전합니다.",
                f"{media_name} 특파원이 {event_id}에 대해 현장에서 전해드립니다."
            ]
            
            article_text = random.choice(article_templates)
            
            news = {
                'news_id': news_id,
                'simulation_id': simulation_id,
                'event_id': event_id,
                'media_name': media_name,
                'article_text': article_text,
                'outlet_bias': outlet_bias,
                'outlet_credibility': outlet_credibility,
                'created_at': created_at.isoformat(),
                'view_count': random.randint(100, 10000),
                'share_count': random.randint(10, 1000)
            }
            news_list.append(news)
        
        return news_list
    
    def generate_snapshot_data(self, simulation_id: str, num_snapshots: int = 5) -> List[Dict[str, Any]]:
        """스냅샷 데이터 생성"""
        snapshots = []
        
        for i in range(num_snapshots):
            snapshot_id = f"snapshot-{simulation_id}-{i+1:03d}"
            created_at = datetime.now() - timedelta(minutes=random.randint(5, 120))
            
            # 주식 가격 데이터 생성
            stocks = {}
            for code in self.stock_codes[:5]:  # 상위 5개 종목만
                base_price = random.randint(30000, 200000)
                change_rate = round(random.uniform(-0.05, 0.05), 3)
                current_price = int(base_price * (1 + change_rate))
                
                stocks[code] = {
                    'code': code,
                    'name': self.stock_names.get(code, f'종목{code}'),
                    'price': current_price,
                    'change': change_rate,
                    'volume': random.randint(1000, 100000),
                    'market_cap': random.randint(1000000000, 100000000000)
                }
            
            # 시장 파라미터 생성
            market_params = {
                'government': {
                    'policy_direction': round(random.uniform(-1.0, 1.0), 2),
                    'interest_rate': round(random.uniform(1.0, 5.0), 2),
                    'tax_policy': round(random.uniform(-0.5, 0.5), 2)
                },
                'company': {
                    'trait': round(random.uniform(-1.0, 1.0), 2),
                    'rnd_ratio': round(random.uniform(0.1, 0.8), 2),
                    'industry_match': round(random.uniform(0.3, 1.0), 2)
                },
                'public': {
                    'risk_appetite': round(random.uniform(-1.0, 1.0), 2),
                    'news_sensitivity': round(random.uniform(0.1, 1.0), 2)
                },
                'media': {
                    'bias': round(random.uniform(-0.5, 0.5), 2),
                    'trust': round(random.uniform(0.3, 0.9), 2)
                }
            }
            
            snapshot = {
                'snapshot_id': snapshot_id,
                'simulation_id': simulation_id,
                'stocks': stocks,
                'market_params': market_params,
                'created_at': created_at.isoformat(),
                'market_index': round(random.uniform(2000, 3000), 2),
                'volatility': round(random.uniform(0.1, 0.5), 3)
            }
            snapshots.append(snapshot)
        
        return snapshots
    
    def generate_all_test_data(self, num_simulations: int = 5) -> Dict[str, Any]:
        """전체 테스트 데이터 생성"""
        print(f"🧪 {num_simulations}개 시뮬레이션에 대한 테스트 데이터 생성 중...")
        
        all_data = {
            'simulations': [],
            'events': [],
            'news': [],
            'snapshots': [],
            'statistics': {}
        }
        
        # 시뮬레이션 데이터 생성
        simulations = self.generate_simulation_data(num_simulations)
        all_data['simulations'] = simulations
        
        total_events = 0
        total_news = 0
        total_snapshots = 0
        
        # 각 시뮬레이션별 데이터 생성
        for sim in simulations:
            sim_id = sim['simulation_id']
            
            # 이벤트 데이터
            events = self.generate_event_data(sim_id, random.randint(5, 15))
            all_data['events'].extend(events)
            total_events += len(events)
            
            # 각 이벤트별 뉴스 데이터
            for event in events:
                news = self.generate_news_data(sim_id, event['event_id'], random.randint(2, 4))
                all_data['news'].extend(news)
                total_news += len(news)
            
            # 스냅샷 데이터
            snapshots = self.generate_snapshot_data(sim_id, random.randint(3, 8))
            all_data['snapshots'].extend(snapshots)
            total_snapshots += len(snapshots)
        
        # 통계 정보 생성
        all_data['statistics'] = {
            'total_simulations': len(simulations),
            'total_events': total_events,
            'total_news': total_news,
            'total_snapshots': total_snapshots,
            'generated_at': datetime.now().isoformat(),
            'simulation_details': [
                {
                    'simulation_id': sim['simulation_id'],
                    'events_count': len([e for e in all_data['events'] if e['simulation_id'] == sim['simulation_id']]),
                    'news_count': len([n for n in all_data['news'] if n['simulation_id'] == sim['simulation_id']]),
                    'snapshots_count': len([s for s in all_data['snapshots'] if s['simulation_id'] == sim['simulation_id']]),
                    'last_activity': sim['updated_at']
                }
                for sim in simulations
            ]
        }
        
        print(f"✅ 테스트 데이터 생성 완료!")
        print(f"  - 시뮬레이션: {len(simulations)}개")
        print(f"  - 이벤트: {total_events}개")
        print(f"  - 뉴스: {total_news}개")
        print(f"  - 스냅샷: {total_snapshots}개")
        
        return all_data
    
    def save_to_tsv(self, data: Dict[str, Any], filename_prefix: str = "test_data"):
        """데이터를 TSV 형식으로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 시뮬레이션 데이터 TSV
        sim_file = self.output_dir / f"{filename_prefix}_simulations_{timestamp}.tsv"
        with open(sim_file, 'w', newline='', encoding='utf-8') as f:
            if data['simulations']:
                writer = csv.DictWriter(f, fieldnames=data['simulations'][0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(data['simulations'])
        
        # 이벤트 데이터 TSV
        event_file = self.output_dir / f"{filename_prefix}_events_{timestamp}.tsv"
        with open(event_file, 'w', newline='', encoding='utf-8') as f:
            if data['events']:
                writer = csv.DictWriter(f, fieldnames=data['events'][0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(data['events'])
        
        # 뉴스 데이터 TSV
        news_file = self.output_dir / f"{filename_prefix}_news_{timestamp}.tsv"
        with open(news_file, 'w', newline='', encoding='utf-8') as f:
            if data['news']:
                writer = csv.DictWriter(f, fieldnames=data['news'][0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(data['news'])
        
        # 스냅샷 데이터 TSV
        snapshot_file = self.output_dir / f"{filename_prefix}_snapshots_{timestamp}.tsv"
        with open(snapshot_file, 'w', newline='', encoding='utf-8') as f:
            if data['snapshots']:
                writer = csv.DictWriter(f, fieldnames=data['snapshots'][0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(data['snapshots'])
        
        return {
            'simulations': str(sim_file),
            'events': str(event_file),
            'news': str(news_file),
            'snapshots': str(snapshot_file)
        }
    
    def save_to_json(self, data: Dict[str, Any], filename_prefix: str = "test_data"):
        """데이터를 JSON 형식으로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 전체 데이터 JSON
        json_file = self.output_dir / f"{filename_prefix}_complete_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 통계만 별도 JSON
        stats_file = self.output_dir / f"{filename_prefix}_statistics_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(data['statistics'], f, ensure_ascii=False, indent=2)
        
        return {
            'complete': str(json_file),
            'statistics': str(stats_file)
        }


def run_data_generation_test():
    """데이터 생성 테스트 실행"""
    print("🧪 테스트 데이터 생성기 실행")
    print("=" * 60)
    
    # 데이터 생성기 초기화
    generator = TestDataGenerator()
    
    # 테스트 데이터 생성
    data = generator.generate_all_test_data(num_simulations=3)
    
    # TSV 파일로 저장
    tsv_files = generator.save_to_tsv(data, "database_test")
    
    # JSON 파일로 저장
    json_files = generator.save_to_json(data, "database_test")
    
    print(f"\n📁 생성된 파일들:")
    print(f"TSV 파일:")
    for key, filepath in tsv_files.items():
        print(f"  - {key}: {filepath}")
    
    print(f"\nJSON 파일:")
    for key, filepath in json_files.items():
        print(f"  - {key}: {filepath}")
    
    print(f"\n📊 통계 요약:")
    stats = data['statistics']
    print(f"  - 시뮬레이션: {stats['total_simulations']}개")
    print(f"  - 이벤트: {stats['total_events']}개")
    print(f"  - 뉴스: {stats['total_news']}개")
    print(f"  - 스냅샷: {stats['total_snapshots']}개")
    
    return {
        'tsv_files': tsv_files,
        'json_files': json_files,
        'statistics': stats
    }


if __name__ == "__main__":
    run_data_generation_test()
