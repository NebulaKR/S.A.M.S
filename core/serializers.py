# core/serializers.py
from typing import Any, Dict, List
from core.entities import News, Public, Company, Government  # 경로는 프로젝트 구조에 맞게 수정

# --- to_dict ---
def news_to_dict(n: News) -> Dict[str, Any]:
    return {
        "bias": float(n.bias),
        "credibility": float(n.credibility),
        "impact_level": int(n.impact_level),
        "category": str(n.category),
        "sentiment": float(n.sentiment),
    }

def public_to_dict(p: Public) -> Dict[str, Any]:
    return {
        "consumer_index": float(p.consumer_index),
        "risk_appetite": float(p.risk_appetite),
        "news_sensitivity": float(p.news_sensitivity),
    }

def company_to_dict(c: Company) -> Dict[str, Any]:
    return {
        "industry": str(c.industry),
        "orientation": float(c.orientation),
        "size": str(c.size),
        "rnd_focus": float(c.rnd_focus),
        "volatility": float(c.volatility),
    }

def government_to_dict(g: Government) -> Dict[str, Any]:
    return {
        "policy_direction": float(g.policy_direction),
        "interest_rate": float(g.interest_rate),
        "tax_policy": float(g.tax_policy),
        "industry_support": dict(g.industry_support or {}),
    }

# --- from_dict ---
def news_from_dict(d: Dict[str, Any]) -> News:
    return News(
        bias=float(d.get("bias", 0.0)),
        credibility=float(d.get("credibility", 0.0)),
        impact_level=int(d.get("impact_level", 0)),
        category=str(d.get("category", "")),
        sentiment=float(d.get("sentiment", 0.0)),
    )

def public_from_dict(d: Dict[str, Any]) -> Public:
    return Public(
        consumer_index=float(d.get("consumer_index", 0.0)),
        risk_appetite=float(d.get("risk_appetite", 0.0)),
        news_sensitivity=float(d.get("news_sensitivity", 0.0)),
    )

def company_from_dict(d: Dict[str, Any]) -> Company:
    return Company(
        industry=str(d.get("industry", "")),
        orientation=float(d.get("orientation", 0.0)),
        size=str(d.get("size", "")),
        rnd_focus=float(d.get("rnd_focus", 0.0)),
        volatility=float(d.get("volatility", 0.0)),
    )

def government_from_dict(d: Dict[str, Any]) -> Government:
    return Government(
        policy_direction=float(d.get("policy_direction", 0.0)),
        interest_rate=float(d.get("interest_rate", 0.0)),
        tax_policy=float(d.get("tax_policy", 0.0)),
        industry_support=dict(d.get("industry_support", {})),
    )
