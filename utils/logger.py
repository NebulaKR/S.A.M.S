from typing import Any, Dict, Optional, List
from datetime import datetime
from utils.firebase import get_firestore

# 경로 구조(권장):
# simulations/{sim_id}/snapshots/{snapshot_id}
# simulations/{sim_id}/events/{event_id}

def save_market_snapshot(
    sim_id: str,
    *,
    stocks: Dict[str, Any],
    market_params: Dict[str, Any],
    simulation_time: datetime,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    """
    '이벤트가 발생한 시점'의 시장 상태(스냅샷)만 저장한다.
    이벤트 내용은 저장하지 않는다.
    """
    db = get_firestore()
    doc_ref = (
        db.collection("simulations")
          .document(sim_id)
          .collection("snapshots")
          .document()  # 자동 ID
    )
    payload = {
        "stocks": stocks,                   # 현재 종목별 가격/체결 등 상태
        "market_params": market_params,     # public/government/company 등 엔진 파라미터
        "simulation_time": simulation_time.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "meta": meta or {},
    }
    doc_ref.set(payload)
    return doc_ref.id


def save_event_log(
    sim_id: str,
    *,
    event_id: str,
    event_payload: Dict[str, Any],
    affected_stocks: list[str],
    market_impact: float,
    simulation_time: datetime,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    """
    발생한 '사건(Event)'을 별도 컬렉션에 저장한다.
    나중에 프롬프트 컨텍스트로 재사용하기 위해 본문/카테고리/감성/영향도 등 원문 필드를 보관.
    """
    db = get_firestore()
    doc_ref = (
        db.collection("simulations")
          .document(sim_id)
          .collection("events")
          .document(event_id)  # 이벤트 ID를 문서 ID로 재사용(중복 방지)
    )
    payload = {
        "event": event_payload,             # Event 객체를 dict로 변환한 내용
        "affected_stocks": affected_stocks,
        "market_impact": float(market_impact),
        "simulation_time": simulation_time.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "meta": meta or {},
    }
    doc_ref.set(payload)
    return doc_ref.id

# 이벤트 로그 조회 함수들
def get_event_log(sim_id: str, event_id: str) -> Optional[Dict[str, Any]]:
    """
    특정 이벤트 로그를 조회한다.
    """
    try:
        db = get_firestore()
        doc = (
            db.collection("simulations")
              .document(sim_id)
              .collection("events")
              .document(event_id)
              .get()
        )
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"이벤트 로그 조회 중 오류: {e}")
        return None

def list_event_logs(
    sim_id: str,
    *,
    limit: int = 20,
    start_after_created_at: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    시뮬레이션의 이벤트 로그 목록을 조회한다.
    """
    try:
        db = get_firestore()
        col = (
            db.collection("simulations")
              .document(sim_id)
              .collection("events")
              .order_by("created_at", direction="DESCENDING")
        )
        
        if start_after_created_at:
            col = col.start_after({"created_at": start_after_created_at})
        
        col = col.limit(limit)
        return [doc.to_dict() for doc in col.stream()]
    except Exception as e:
        print(f"이벤트 로그 목록 조회 중 오류: {e}")
        return []

def get_recent_events_for_context(sim_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    뉴스 생성 컨텍스트용으로 최근 이벤트들을 조회한다.
    """
    try:
        db = get_firestore()
        docs = (
            db.collection("simulations")
              .document(sim_id)
              .collection("events")
              .order_by("created_at", direction="DESCENDING")
              .limit(limit)
              .stream()
        )
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"최근 이벤트 조회 중 오류: {e}")
        return []

def save_news_article(
    sim_id: str,
    *,
    event_id: str,
    news_id: str,
    media_name: str,
    article_text: str,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    """
    생성된 뉴스 기사를 저장한다.
    """
    try:
        db = get_firestore()
        doc_ref = (
            db.collection("simulations")
              .document(sim_id)
              .collection("events")
              .document(event_id)
              .collection("news")
              .document(news_id)
        )
        payload = {
            "news_id": news_id,
            "media_name": media_name,
            "article_text": article_text,
            "created_at": datetime.utcnow().isoformat(),
            "meta": meta or {},
        }
        doc_ref.set(payload)
        return doc_ref.id
    except Exception as e:
        print(f"뉴스 기사 저장 중 오류: {e}")
        return ""

def get_news_articles_for_event(sim_id: str, event_id: str) -> List[Dict[str, Any]]:
    """
    특정 이벤트에 대한 뉴스 기사들을 조회한다.
    """
    try:
        db = get_firestore()
        docs = (
            db.collection("simulations")
              .document(sim_id)
              .collection("events")
              .document(event_id)
              .collection("news")
              .order_by("created_at", direction="DESCENDING")
              .stream()
        )
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"뉴스 기사 조회 중 오류: {e}")
        return []

def get_recent_market_snapshots(sim_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    특정 시뮬레이션의 최근 시장 스냅샷들을 조회한다.
    
    Args:
        sim_id: 시뮬레이션 ID
        limit: 조회할 스냅샷 수
    
    Returns:
        최근 시장 스냅샷 목록
    """
    try:
        db = get_firestore()
        docs = (
            db.collection("simulations")
              .document(sim_id)
              .collection("snapshots")
              .order_by("created_at", direction="DESCENDING")
              .limit(limit)
              .stream()
        )
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"시장 스냅샷 조회 중 오류: {e}")
        return []

def get_all_events_across_simulations(limit: int = 1000) -> List[Dict[str, Any]]:
    """
    모든 시뮬레이션에서 발생한 이벤트들을 조회한다.
    
    Args:
        limit: 조회할 이벤트 수 (기본값: 1000)
    
    Returns:
        모든 이벤트 목록 (시뮬레이션 ID 포함)
    """
    try:
        db = get_firestore()
        
        # Firebase 연결 상태 확인
        if db is None:
            print("❌ Firebase가 연결되지 않았습니다. 이벤트 조회 불가.")
            return []
        
        all_events = []
        
        # 모든 시뮬레이션 문서 조회
        sim_docs = db.collection("simulations").stream()
        
        for sim_doc in sim_docs:
            sim_id = sim_doc.id
            # 각 시뮬레이션의 이벤트들 조회
            event_docs = (
                sim_doc.reference
                .collection("events")
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            
            for event_doc in event_docs:
                event_data = event_doc.to_dict()
                event_data['simulation_id'] = sim_id  # 시뮬레이션 ID 추가
                all_events.append(event_data)
        
        # 전체를 생성 시간순으로 정렬하고 limit 적용
        all_events.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return all_events[:limit]
        
    except Exception as e:
        print(f"전체 이벤트 조회 중 오류: {e}")
        return []

def get_all_news_across_simulations(limit: int = 1000) -> List[Dict[str, Any]]:
    """
    모든 시뮬레이션에서 생성된 뉴스 기사들을 조회한다.
    
    Args:
        limit: 조회할 뉴스 수 (기본값: 1000)
    
    Returns:
        모든 뉴스 목록 (시뮬레이션 ID와 이벤트 ID 포함)
    """
    try:
        db = get_firestore()
        
        # Firebase 연결 상태 확인
        if db is None:
            print("❌ Firebase가 연결되지 않았습니다. 뉴스 조회 불가.")
            return []
        
        all_news = []
        
        # 모든 시뮬레이션 문서 조회
        sim_docs = db.collection("simulations").stream()
        
        for sim_doc in sim_docs:
            sim_id = sim_doc.id
            # 각 시뮬레이션의 이벤트들 조회
            event_docs = sim_doc.reference.collection("events").stream()
            
            for event_doc in event_docs:
                event_id = event_doc.id
                # 각 이벤트의 뉴스들 조회
                news_docs = (
                    event_doc.reference
                    .collection("news")
                    .order_by("created_at", direction="DESCENDING")
                    .stream()
                )
                
                for news_doc in news_docs:
                    news_data = news_doc.to_dict()
                    news_data['simulation_id'] = sim_id  # 시뮬레이션 ID 추가
                    news_data['event_id'] = event_id     # 이벤트 ID 추가
                    all_news.append(news_data)
        
        # 전체를 생성 시간순으로 정렬하고 limit 적용
        all_news.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return all_news[:limit]
        
    except Exception as e:
        print(f"전체 뉴스 조회 중 오류: {e}")
        return []

def get_database_statistics() -> Dict[str, Any]:
    """
    전체 데이터베이스의 통계 정보를 조회한다.
    
    Returns:
        데이터베이스 통계 정보
    """
    try:
        print("🔍 데이터베이스 통계 조회 시작...")
        db = get_firestore()
        
        # Firebase 연결 상태 확인
        if db is None:
            print("❌ Firebase가 연결되지 않았습니다. 개발 모드로 실행 중입니다.")
            return {
                'total_simulations': 0,
                'total_events': 0,
                'total_news': 0,
                'total_snapshots': 0,
                'simulation_details': [],
                'error': 'Firebase 연결되지 않음 (개발 모드)',
                'firebase_status': 'disconnected'
            }
        
        stats = {
            'total_simulations': 0,
            'total_events': 0,
            'total_news': 0,
            'total_snapshots': 0,
            'simulation_details': [],
            'firebase_status': 'connected'
        }
        
        # 모든 시뮬레이션 문서 조회
        print("📊 시뮬레이션 컬렉션 조회 중...")
        try:
            sim_docs = list(db.collection("simulations").stream())
            print(f"📊 발견된 시뮬레이션 수: {len(sim_docs)}")
        except Exception as e:
            print(f"❌ 시뮬레이션 컬렉션 조회 실패: {e}")
            return {
                'total_simulations': 0,
                'total_events': 0,
                'total_news': 0,
                'total_snapshots': 0,
                'simulation_details': [],
                'error': f'시뮬레이션 컬렉션 조회 실패: {str(e)}',
                'firebase_status': 'error'
            }
        
        for sim_doc in sim_docs:
            sim_id = sim_doc.id
            print(f"🔍 시뮬레이션 {sim_id} 분석 중...")
            sim_stats = {
                'simulation_id': sim_id,
                'events_count': 0,
                'news_count': 0,
                'snapshots_count': 0,
                'last_activity': None
            }
            
            # 이벤트 수 계산
            try:
                events = list(sim_doc.reference.collection("events").stream())
                sim_stats['events_count'] = len(events)
                stats['total_events'] += len(events)
                print(f"  📝 이벤트 수: {len(events)}")
            except Exception as e:
                print(f"  ❌ 이벤트 조회 오류: {e}")
            
            # 뉴스 수 계산
            try:
                total_news = 0
                for event in events:
                    try:
                        news_count = len(list(event.reference.collection("news").stream()))
                        total_news += news_count
                    except Exception as e:
                        print(f"    ❌ 뉴스 조회 오류 (이벤트 {event.id}): {e}")
                sim_stats['news_count'] = total_news
                stats['total_news'] += total_news
                print(f"  📰 뉴스 수: {total_news}")
            except Exception as e:
                print(f"  ❌ 뉴스 계산 오류: {e}")
            
            # 스냅샷 수 계산
            try:
                snapshots = list(sim_doc.reference.collection("snapshots").stream())
                sim_stats['snapshots_count'] = len(snapshots)
                stats['total_snapshots'] += len(snapshots)
                print(f"  📊 스냅샷 수: {len(snapshots)}")
            except Exception as e:
                print(f"  ❌ 스냅샷 조회 오류: {e}")
            
            # 마지막 활동 시간 계산
            try:
                all_times = []
                for event in events:
                    event_data = event.to_dict()
                    if 'created_at' in event_data:
                        all_times.append(event_data['created_at'])
                for snapshot in snapshots:
                    snapshot_data = snapshot.to_dict()
                    if 'created_at' in snapshot_data:
                        all_times.append(snapshot_data['created_at'])
                
                if all_times:
                    all_times.sort(reverse=True)
                    sim_stats['last_activity'] = all_times[0]
            except Exception as e:
                print(f"  ❌ 시간 계산 오류: {e}")
            
            stats['simulation_details'].append(sim_stats)
            stats['total_simulations'] += 1
        
        print(f"✅ 통계 조회 완료: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ 데이터베이스 통계 조회 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_simulations': 0,
            'total_events': 0,
            'total_news': 0,
            'total_snapshots': 0,
            'simulation_details': [],
            'error': str(e),
            'firebase_status': 'error'
        }
