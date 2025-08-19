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


def _to01_from_signed(x: float) -> float:
	"""-1~+1 범위를 0~1 범위로 선형 변환."""
	return _clamp01((float(x) + 1.0) / 2.0)


def main_model(
	weights: Dict[str, float],
	params: Dict,
	events: Dict,
	base_price: float = 100.0,
	external: Optional[Dict] = None,
	ml_model_path: Optional[str] = None,
	ml_blend_weight: float = 0.0,
) -> Dict[str, float]:
	"""
	코치가 전달한 가중치와 내부 파라미터, 이벤트 정보를 종합하여
	최종 변동률(delta)과 가격(price)을 계산한다.

	옵션:
	- ml_model_path: 학습된 모델 경로(json). 주어지면 params/events로 예측한 delta와 블렌딩
	- ml_blend_weight: 0~1, 1이면 ML만 사용, 0이면 규칙기반만 사용
	"""

	# 방어적 정규화 (코치에서 이미 정규화해도, 안전망으로 한 번 더 적용)
	w = _normalize({
		"w_news": float(weights.get("w_news", 0.25)),
		"w_public": float(weights.get("w_public", 0.25)),
		"w_company": float(weights.get("w_company", 0.25)),
		"w_gov": float(weights.get("w_gov", 0.25)),
	})

	# 파라미터: dict 또는 엔티티 지원
	p = params.get("public", {})
	c = params.get("company", {})
	g = params.get("government", {})

	if hasattr(p, "risk_appetite"):
		risk_appetite = _to01_from_signed(getattr(p, "risk_appetite", 0.0))
	else:
		risk_appetite = _to01_from_signed(float(p.get("risk_appetite", 0.0)))

	# 회사 성향: trait(0~1) or orientation(-1~+1)
	if hasattr(c, "orientation"):
		comp_trait = _to01_from_signed(getattr(c, "orientation", 0.0))
	else:
		comp_trait = _clamp01(float(c.get("trait", 0.5)))

	if hasattr(g, "policy_direction"):
		policy_direction = _to01_from_signed(getattr(g, "policy_direction", 0.0))
	else:
		policy_direction = _clamp01(float(g.get("policy_direction", 0.5)))

	# 이벤트 클리핑: 미디어 신뢰도 보정 지원
	news_impact = _clamp01(float(events.get("news_impact", 0.0)))
	media_cred = _clamp01(float(events.get("media_credibility", 1.0)))

	# 효과 계산 (규칙기반)
	news_effect = w["w_news"] * news_impact * media_cred
	public_effect = w["w_public"] * risk_appetite
	comp_effect = w["w_company"] * comp_trait
	gov_effect = w["w_gov"] * policy_direction
	rule_delta = news_effect + public_effect + comp_effect + gov_effect

	# ML 예측과 블렌딩(옵션)
	final_delta = rule_delta
	if ml_model_path and ml_blend_weight > 0.0:
		try:
			from utils.inference import predict_delta_with_model, blend_deltas
			ml_delta = float(predict_delta_with_model(ml_model_path, params, events))
			final_delta = blend_deltas(rule_delta, ml_delta, weight_ml=ml_blend_weight)
		except Exception:
			# 실패 시 규칙기반 유지
			final_delta = rule_delta

	# 반올림 규칙 적용
	final_delta = round(final_delta, 4)
	new_price = round(base_price * (1.0 + final_delta), 2)

	return {"delta": final_delta, "price": new_price} 