#!/usr/bin/env python3
"""
Firebase 모킹 시스템
실제 Firebase API 호출 없이 테스트할 수 있는 모킹 클래스들
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class MockFirestoreDocument:
    """Firestore 문서를 모킹하는 클래스"""
    
    def __init__(self, doc_id: str, data: Dict[str, Any]):
        self.id = doc_id
        self._data = data
        self._reference = None
    
    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()
    
    def exists(self) -> bool:
        return self._data is not None
    
    @property
    def reference(self):
        if self._reference is None:
            self._reference = MockFirestoreDocumentReference(self.id, self._data)
        return self._reference


class MockFirestoreDocumentReference:
    """Firestore 문서 참조를 모킹하는 클래스"""
    
    def __init__(self, doc_id: str, data: Dict[str, Any]):
        self.id = doc_id
        self._data = data
        self._parent = None
    
    def get(self) -> MockFirestoreDocument:
        return MockFirestoreDocument(self.id, self._data)
    
    def set(self, data: Dict[str, Any], merge: bool = False):
        if merge:
            self._data.update(data)
        else:
            self._data = data
    
    def collection(self, collection_name: str):
        return MockFirestoreCollection(collection_name, self.id)
    
    @property
    def parent(self):
        return self._parent


class MockFirestoreCollection:
    """Firestore 컬렉션을 모킹하는 클래스"""
    
    def __init__(self, collection_name: str, parent_id: str = None):
        self.collection_name = collection_name
        self.parent_id = parent_id
        self._documents = {}
        self._query_filters = []
        self._order_by = None
        self._limit_count = None
    
    def document(self, doc_id: str = None):
        if doc_id is None:
            doc_id = f"auto_{int(time.time() * 1000)}"
        
        if doc_id not in self._documents:
            self._documents[doc_id] = {}
        
        return MockFirestoreDocumentReference(doc_id, self._documents[doc_id])
    
    def add(self, data: Dict[str, Any]) -> MockFirestoreDocumentReference:
        doc_id = f"auto_{int(time.time() * 1000)}"
        self._documents[doc_id] = data
        return MockFirestoreDocumentReference(doc_id, data)
    
    def stream(self):
        """컬렉션의 모든 문서를 스트림으로 반환"""
        for doc_id, data in self._documents.items():
            yield MockFirestoreDocument(doc_id, data)
    
    def where(self, field: str, operator: str, value: Any):
        """WHERE 조건 추가"""
        self._query_filters.append((field, operator, value))
        return self
    
    def order_by(self, field: str, direction: str = "ASCENDING"):
        """ORDER BY 조건 추가"""
        self._order_by = (field, direction)
        return self
    
    def limit(self, count: int):
        """LIMIT 조건 추가"""
        self._limit_count = count
        return self
    
    def start_after(self, cursor_data: Dict[str, Any]):
        """커서 기반 페이징"""
        # 간단한 구현 - 실제로는 더 복잡한 로직 필요
        return self


class MockFirestore:
    """Firestore 클라이언트를 모킹하는 클래스"""
    
    def __init__(self):
        self._collections = {}
        self._collection_groups = {}
    
    def collection(self, collection_name: str):
        if collection_name not in self._collections:
            self._collections[collection_name] = MockFirestoreCollection(collection_name)
        return self._collections[collection_name]
    
    def collection_group(self, collection_name: str):
        """컬렉션 그룹 조회 (모든 시뮬레이션의 특정 컬렉션)"""
        if collection_name not in self._collection_groups:
            self._collection_groups[collection_name] = []
        
        # 모든 시뮬레이션의 해당 컬렉션에서 문서 수집
        all_docs = []
        for sim_id, sim_collection in self._collections.get('simulations', {}).items():
            if hasattr(sim_collection, '_documents'):
                for doc_id, doc_data in sim_collection._documents.items():
                    all_docs.append(MockFirestoreDocument(doc_id, doc_data))
        
        return all_docs


class MockFirebaseAdmin:
    """Firebase Admin을 모킹하는 클래스"""
    
    def __init__(self):
        self._apps_list = []
        self._initialized = False
    
    def initialize_app(self, cred, options=None):
        self._initialized = True
        self._apps_list.append({
            'cred': cred,
            'options': options
        })
    
    @property
    def _apps(self):
        return self._apps_list if self._initialized else []


class MockFirebaseSystem:
    """전체 Firebase 시스템을 모킹하는 클래스"""
    
    def __init__(self):
        self.firestore = MockFirestore()
        self.admin = MockFirebaseAdmin()
        self._test_data_loaded = False
    
    def load_test_data(self, data_file: str = None):
        """테스트 데이터 로드"""
        if self._test_data_loaded:
            return
        
        # 기본 테스트 데이터 생성
        self._generate_default_test_data()
        self._test_data_loaded = True
    
    def _generate_default_test_data(self):
        """기본 테스트 데이터 생성"""
        # 시뮬레이션 데이터
        sim_collection = self.firestore.collection('simulations')
        
        for i in range(3):
            sim_id = f"test-sim-{i+1}"
            sim_doc = sim_collection.document(sim_id)
            sim_doc.set({
                'sim_id': sim_id,
                'name': f'테스트 시뮬레이션 {i+1}',
                'status': 'running' if i < 2 else 'stopped',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            # 이벤트 데이터
            events_collection = sim_doc.collection('events')
            for j in range(5):
                event_id = f"event-{i+1}-{j+1}"
                event_doc = events_collection.document(event_id)
                event_doc.set({
                    'event_id': event_id,
                    'event_type': f'테스트 이벤트 {j+1}',
                    'category': ['경제', '정책', '기업', '기술', '국제'][j % 5],
                    'sentiment': round((j - 2) * 0.3, 2),
                    'impact_level': (j % 5) + 1,
                    'affected_stocks': [f'005930', f'005380', f'005490'][:j+1],
                    'market_impact': round((j - 2) * 0.1, 3),
                    'created_at': datetime.now().isoformat()
                })
                
                # 뉴스 데이터
                news_collection = event_doc.collection('news')
                for k in range(2 + (j % 2)):
                    news_id = f"news-{i+1}-{j+1}-{k+1}"
                    news_doc = news_collection.document(news_id)
                    news_doc.set({
                        'news_id': news_id,
                        'media_name': ['조선일보', '중앙일보', '한국경제', '매일경제'][k % 4],
                        'article_text': f'테스트 뉴스 기사 {j+1}-{k+1}: {event_id}에 대한 보도',
                        'outlet_bias': round((k - 1) * 0.2, 2),
                        'outlet_credibility': round(0.6 + (k * 0.1), 2),
                        'created_at': datetime.now().isoformat()
                    })
            
            # 스냅샷 데이터
            snapshots_collection = sim_doc.collection('snapshots')
            for j in range(5):
                snapshot_id = f"snapshot-{i+1}-{j+1}"
                snapshot_doc = snapshots_collection.document(snapshot_id)
                snapshot_doc.set({
                    'snapshot_id': snapshot_id,
                    'stocks': {
                        '005930': {'price': 75000 + (j * 1000), 'change': j * 0.5},
                        '005380': {'price': 45000 + (j * 500), 'change': j * 0.3},
                        '005490': {'price': 85000 + (j * 800), 'change': j * 0.4}
                    },
                    'market_params': {
                        'government': {'policy_direction': 0.2, 'interest_rate': 3.0},
                        'company': {'trait': 0.4, 'rnd_ratio': 0.3},
                        'public': {'risk_appetite': 0.3, 'news_sensitivity': 0.7}
                    },
                    'created_at': datetime.now().isoformat()
                })
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 생성"""
        sim_collection = self.firestore.collection('simulations')
        sim_docs = list(sim_collection.stream())
        
        total_events = 0
        total_news = 0
        total_snapshots = 0
        simulation_details = []
        
        for sim_doc in sim_docs:
            sim_id = sim_doc.id
            
            # 이벤트 수 계산
            events_collection = sim_doc.reference.collection('events')
            events = list(events_collection.stream())
            events_count = len(events)
            total_events += events_count
            
            # 뉴스 수 계산
            news_count = 0
            for event in events:
                news_collection = event.reference.collection('news')
                news = list(news_collection.stream())
                news_count += len(news)
            total_news += news_count
            
            # 스냅샷 수 계산
            snapshots_collection = sim_doc.reference.collection('snapshots')
            snapshots = list(snapshots_collection.stream())
            snapshots_count = len(snapshots)
            total_snapshots += snapshots_count
            
            simulation_details.append({
                'simulation_id': sim_id,
                'events_count': events_count,
                'news_count': news_count,
                'snapshots_count': snapshots_count,
                'last_activity': sim_doc.to_dict().get('updated_at')
            })
        
        return {
            'total_simulations': len(sim_docs),
            'total_events': total_events,
            'total_news': total_news,
            'total_snapshots': total_snapshots,
            'simulation_details': simulation_details,
            'firebase_status': 'connected'
        }


# 전역 모킹 인스턴스
mock_firebase = MockFirebaseSystem()


def get_mock_firestore():
    """모킹된 Firestore 클라이언트 반환"""
    mock_firebase.load_test_data()
    return mock_firebase.firestore


def get_mock_firebase_admin():
    """모킹된 Firebase Admin 반환"""
    return mock_firebase.admin


def get_mock_statistics():
    """모킹된 통계 데이터 반환"""
    mock_firebase.load_test_data()
    return mock_firebase.get_statistics()


if __name__ == "__main__":
    # 테스트 실행
    print("🧪 Firebase 모킹 시스템 테스트")
    print("=" * 50)
    
    # 테스트 데이터 로드
    mock_firebase.load_test_data()
    
    # 통계 조회
    stats = mock_firebase.get_statistics()
    
    print(f"📊 생성된 데이터:")
    print(f"  - 시뮬레이션: {stats['total_simulations']}개")
    print(f"  - 이벤트: {stats['total_events']}개")
    print(f"  - 뉴스: {stats['total_news']}개")
    print(f"  - 스냅샷: {stats['total_snapshots']}개")
    
    print(f"\n📋 시뮬레이션별 상세:")
    for detail in stats['simulation_details']:
        print(f"  - {detail['simulation_id']}: {detail['events_count']} 이벤트, {detail['news_count']} 뉴스, {detail['snapshots_count']} 스냅샷")
    
    print(f"\n✅ Firebase 모킹 시스템 테스트 완료!")
