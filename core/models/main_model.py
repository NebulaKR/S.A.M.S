from typing import Dict, Optional


def _clamp01(value: float) -> float:
    """[0,1] 범위로 클리핑."""
    if value is None:
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _normalize(weights: Dict[str, float]) -> Dict[str, float]:
    """가중치 합이 1이 되도록 정규화. 모두 0이면 균등 분배."""
    total = sum(weights.values())
    if total == 0:
        n = len(weights)
        if n == 0:
            return weights
        equal = round(1.0 / n, 6)
        return {k: equal for k in weights}
    return {k: (v / total) for k, v in weights.items()}


def main_model(
    weights: Dict[str, float],
    params: Dict,
    events: Dict,
    base_price: float = 100.0,
    external: Optional[Dict] = None,
) -> Dict[str, float]:
    """
    코치가 전달한 가중치와 내부 파라미터, 이벤트 정보를 종합하여
    최종 변동률(delta)과 가격(price)을 계산한다.

    MVP 계산식:
        news_effect   = w_news    * events["news_impact"]
        public_effect = w_public  * params["public"]["risk_appetite"]
        comp_effect   = w_company * params["company"]["trait"]
        gov_effect    = w_gov     * params["government"]["policy_direction"]
        delta = news_effect + public_effect + comp_effect + gov_effect
        new_price = base_price * (1 + delta)

    규칙:
    - 모든 입력 수치는 [0,1]로 클리핑
    - 가중치는 합=1 정규화(방어적 재정규화)
    - delta는 소수점 4자리, price는 소수점 2자리 반올림

    확장 포인트(현재는 미사용):
    - external: {"vix": float, "fx_rate": float, ...}
    - events: {"direct_impact": float, "news_impact": float, ...}

    Returns:
        {"delta": float, "price": float}
    """

    # 방어적 정규화 (코치에서 이미 정규화해도, 안전망으로 한 번 더 적용)
    w = _normalize({
        "w_news": float(weights.get("w_news", 0.25)),
        "w_public": float(weights.get("w_public", 0.25)),
        "w_company": float(weights.get("w_company", 0.25)),
        "w_gov": float(weights.get("w_gov", 0.25)),
    })

    # 파라미터 클리핑
    p = params.get("public", {})
    c = params.get("company", {})
    g = params.get("government", {})

    risk_appetite = _clamp01(float(p.get("risk_appetite", 0.5)))
    trait = _clamp01(float(c.get("trait", 0.5)))
    policy_direction = _clamp01(float(g.get("policy_direction", 0.5)))

    # 이벤트 클리핑
    news_impact = _clamp01(float(events.get("news_impact", 0.0)))

    # MVP 효과 계산
    news_effect = w["w_news"] * news_impact
    public_effect = w["w_public"] * risk_appetite
    comp_effect = w["w_company"] * trait
    gov_effect = w["w_gov"] * policy_direction

    delta = news_effect + public_effect + comp_effect + gov_effect

    # 반올림 규칙 적용
    delta = round(delta, 4)
    new_price = round(base_price * (1.0 + delta), 2)

    return {"delta": delta, "price": new_price} 