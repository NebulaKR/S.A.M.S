# core/repository.py
from typing import Any, Dict, List, Optional, Tuple
from django.utils import timezone  # Django 사용 안 하면 datetime.utcnow().isoformat()으로 대체
from utils.firebase import get_firestore
from core.serializers import (
    news_to_dict, news_from_dict,
    public_to_dict, public_from_dict,
    company_to_dict, company_from_dict,
    government_to_dict, government_from_dict,
)
from core.entities import News, Public, Company, Government  # 경로는 프로젝트 구조에 맞게 수정

def _snapshots(sim_id: str):
    db = get_firestore()
    return db.collection("simulations").document(sim_id).collection("snapshots")

def save_snapshot(
    sim_id: str,
    *,
    news_list: List[News],
    public: Public,
    companies: List[Company],
    government: Government,
    meta: Optional[Dict[str, Any]] = None,
    snapshot_id: Optional[str] = None,  # 지정 시 같은 ID로 upsert
) -> str:
    col = _snapshots(sim_id)
    doc_ref = col.document(snapshot_id) if snapshot_id else col.document()

    payload = {
        "news_list": [news_to_dict(n) for n in news_list],
        "public": public_to_dict(public),
        "companies": [company_to_dict(c) for c in companies],
        "government": government_to_dict(government),
        "meta": meta or {},
        "created_at": timezone.now().isoformat(),
    }

    doc_ref.set(payload)
    return doc_ref.id

def load_snapshot(sim_id: str, snapshot_id: str) -> Dict[str, Any]:
    doc = _snapshots(sim_id).document(snapshot_id).get()
    if not doc.exists:
        raise ValueError(f"snapshot not found: sim_id={sim_id}, snapshot_id={snapshot_id}")
    return doc.to_dict() or {}

def parse_snapshot(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "news_list": [news_from_dict(d) for d in data.get("news_list", [])],
        "public": public_from_dict(data.get("public", {})),
        "companies": [company_from_dict(d) for d in data.get("companies", [])],
        "government": government_from_dict(data.get("government", {})),
        "meta": data.get("meta", {}),
        "created_at": data.get("created_at"),
    }

def get_latest_snapshot(sim_id: str) -> Optional[Dict[str, Any]]:
    # created_at 기준 최신 한 건
    q = _snapshots(sim_id).order_by("created_at", direction="DESCENDING").limit(1).stream()
    for doc in q:
        return doc.to_dict()
    return None

def list_snapshots(
    sim_id: str,
    *,
    limit: int = 20,
    start_after_created_at: Optional[str] = None
) -> List[Dict[str, Any]]:
    # 페이지네이션용 간단 리스트
    col = _snapshots(sim_id).order_by("created_at", direction="DESCENDING")
    if start_after_created_at:
        col = col.start_after({"created_at": start_after_created_at})
    col = col.limit(limit)
    return [doc.to_dict() for doc in col.stream()]
