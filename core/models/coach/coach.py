from typing import Dict, Optional

# 유틸: [0,1] 범위로 클리핑

def _clamp01(value: float) -> float:
    if value is None:
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)

# 유틸: 가중치 정규화 (합=1). 모두 0이면 균등 분배

def _normalize(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(weights.values())
    if total == 0:
        n = len(weights)
        if n == 0:
            return weights
        equal = round(1.0 / n, 6)
        return {k: equal for k in weights}
    return {k: round(v / total, 6) for k, v in weights.items()}


class Coach:
    def __init__(self, internal_params):
        """
        초기화 함수.
        내부 파라미터를 받아 저장함.
        internal_params: dict
            시뮬레이션에서 생성된 정부, 기업, 대중 등의 파라미터 묶음
        """
        self.params = internal_params

    def adjust_weights(
        self,
        events_summary: Optional[Dict] = None,
        external: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """
        내부 파라미터를 기반으로 뉴스, 대중, 기업, 정부 각각에 대한
        주가 반영 가중치를 계산하여 딕셔너리 형태로 반환.

        Requirements:
        1) 각 가중치는 [0,1]로 클리핑
        2) 최종적으로 합=1 정규화
        3) 확장 가능: events_summary, external을 반영할 수 있도록 시그니처 확장

        Returns:
            dict: {
                "w_news": float,
                "w_public": float,
                "w_company": float,
                "w_gov": float
            }
        """

        # 대중(public), 정부(government), 기업(company) 파라미터 분리
        p = self.params.get("public", {})
        g = self.params.get("government", {})
        c = self.params.get("company", {})

        # 원천 값들을 [0,1] 범위로 클리핑하여 안정성 확보
        news_sensitivity = _clamp01(p.get("news_sensitivity", 0.5))
        risk_appetite = _clamp01(p.get("risk_appetite", 0.5))
        rnd_ratio = _clamp01(c.get("rnd_ratio", 0.3))
        policy_direction = _clamp01(g.get("policy_direction", 0.5))

        # 1) 기본 MVP 가중치 계산 (요구식)
        w_news = 0.4 + 0.2 * news_sensitivity
        w_public = 0.3 + 0.1 * risk_appetite
        w_company = 0.2 + 0.2 * rnd_ratio
        w_gov = 0.1 + 0.2 * policy_direction

        # 2) 확장 지점: events_summary / external 반영 (옵션)
        # - 예: 깜짝지표(surprise_ratio)가 크면 뉴스 가중치를 소폭 상향
        if events_summary:
            surprise_ratio = _clamp01(events_summary.get("surprise_ratio", 0.0))
            pos_neg_ratio = _clamp01(events_summary.get("pos_neg_ratio", 0.5))
            w_news += 0.05 * surprise_ratio
            # 대중 심리 양/음 비율이 높을수록 public 가중치 보정
            w_public += 0.05 * (pos_neg_ratio - 0.5)

        # - 외부 변수: 예) VIX(변동성) 높으면 뉴스 민감도 상향, 금리(FX 등) 반영 등
        if external:
            vix = _clamp01(external.get("vix", 0.0))
            w_news += 0.05 * vix

        # 3) [0,1] 클리핑 → 정규화(sum=1)
        clipped = {
            "w_news": _clamp01(w_news),
            "w_public": _clamp01(w_public),
            "w_company": _clamp01(w_company),
            "w_gov": _clamp01(w_gov),
        }
        normalized = _normalize(clipped)

        # 소수 3자리 고정 (기존 출력 가독성 유지)
        return {k: round(v, 3) for k, v in normalized.items()}