from typing import Dict, List, Optional, Tuple, Any


def clamp01(value: float) -> float:
    if value is None:
        return 0.0
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def to01_from_signed(x: float) -> float:
    try:
        return clamp01((float(x) + 1.0) / 2.0)
    except Exception:
        return 0.5


def extract_basic_factors(params: Dict[str, Any], events: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    main_model과 스케일을 일치시키는 기본 요인(feature) 추출기.

    Returns keys:
      - risk_appetite_01, comp_trait_01, policy_direction_01
      - news_impact_01, media_cred_01
      - news_x_media, risk_x_policy (상호작용 예시)
    """
    p = params.get("public", {}) if params else {}
    c = params.get("company", {}) if params else {}
    g = params.get("government", {}) if params else {}

    # public
    risk_appetite_01 = to01_from_signed(p.get("risk_appetite", 0.0))

    # company: orientation(-1~+1) 우선, 없으면 trait(0~1)
    if "orientation" in c:
        comp_trait_01 = to01_from_signed(c.get("orientation", 0.0))
    else:
        comp_trait_01 = clamp01(c.get("trait", 0.5))

    # government
    policy_direction_01 = (
        to01_from_signed(g.get("policy_direction", 0.0))
        if ("policy_direction" in g and isinstance(g.get("policy_direction"), (int, float)))
        else clamp01(g.get("policy_direction", 0.5))
    )

    # events
    events = events or {}
    news_impact_01 = clamp01(events.get("news_impact", 0.0))
    media_cred_01 = clamp01(events.get("media_credibility", events.get("media_trust", 1.0)))

    # interactions
    news_x_media = news_impact_01 * media_cred_01
    risk_x_policy = risk_appetite_01 * policy_direction_01

    return {
        "risk_appetite_01": risk_appetite_01,
        "comp_trait_01": comp_trait_01,
        "policy_direction_01": policy_direction_01,
        "news_impact_01": news_impact_01,
        "media_cred_01": media_cred_01,
        "news_x_media": news_x_media,
        "risk_x_policy": risk_x_policy,
    }


def build_supervised_from_sequence(
    sequence: List[Dict[str, Any]],
    horizon: int = 1,
    label_key_future: str = "realized_delta",
    allow_price_fallback: bool = True,
) -> Tuple[List[Dict[str, float]], List[float], List[Tuple[int, int]]]:
    """
    시계열 레코드 시퀀스에서 누출 없이 (features_t, label_{t+h}) 감독학습용 데이터셋을 생성.

    Args:
      - sequence: 각 시점 dict. 권장 키: {"params", "events", "price"?, "realized_delta"?}
      - horizon: 예측 선행 기간 H
      - label_key_future: 레이블로 사용할 미래 시점의 키(예: realized_delta)
      - allow_price_fallback: true인 경우 t와 t+h의 price로 delta 계산(둘 다 있어야 함)

    Returns:
      - X: feature dict 리스트 (각 항목은 t 시점에서 추출)
      - y: float 리스트 (각 항목은 t+h 시점의 레이블)
      - index_pairs: (t, t+h) 인덱스 매핑 리스트
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    X: List[Dict[str, float]] = []
    y: List[float] = []
    index_pairs: List[Tuple[int, int]] = []

    n = len(sequence)
    for t in range(0, max(0, n - horizon)):
        src = sequence[t]
        tgt = sequence[t + horizon]

        # 1) features from time t
        features = extract_basic_factors(src.get("params", {}), src.get("events", {}))

        # 2) label from time t+h
        label: Optional[float] = None
        if label_key_future in tgt:
            try:
                label = float(tgt[label_key_future])
            except Exception:
                label = None
        if label is None and allow_price_fallback:
            if ("price" in src) and ("price" in tgt):
                try:
                    p0 = float(src["price"])  # price at t
                    p1 = float(tgt["price"])  # price at t+h
                    if p0 > 0.0:
                        label = (p1 / p0) - 1.0
                except Exception:
                    label = None

        # 3) 누락된 레이블은 스킵
        if label is None:
            continue

        X.append(features)
        y.append(float(label))
        index_pairs.append((t, t + horizon))

    return X, y, index_pairs


def build_labels_from_prices(prices: List[float], horizon: int = 1) -> List[Optional[float]]:
    """
    단일 가격 시퀀스에서 선행기간(horizon) 수익률(delta) 라벨 시퀀스를 구성.
    길이는 입력과 동일하며, 각 t에 대해 label_{t} = (price_{t+h}/price_{t}) - 1, 단 t+h가 없으면 None.
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    n = len(prices)
    labels: List[Optional[float]] = [None] * n
    for t in range(n):
        k = t + horizon
        if k >= n:
            break
        try:
            p0 = float(prices[t])
            p1 = float(prices[k])
        except Exception:
            labels[t] = None
            continue
        if p0 <= 0.0:
            labels[t] = None
        else:
            labels[t] = (p1 / p0) - 1.0
    return labels 