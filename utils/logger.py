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
