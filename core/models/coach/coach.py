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
		internal_params: dict 또는 엔티티 딕셔너리
			시뮬레이션에서 생성된 정부, 기업, 대중 등의 파라미터 묶음
		"""
		self.params = internal_params

	def _extract_values(self) -> Dict[str, float]:
		"""dict 또는 엔티티에서 필요한 지표를 [0,1] 스케일로 추출."""
		p = self.params.get("public", {})
		g = self.params.get("government", {})
		c = self.params.get("company", {})
		media = self.params.get("news", {})

		# 엔티티 여부 판단
		is_entity = hasattr(p, "risk_appetite") and hasattr(g, "policy_direction")

		if is_entity:
			news_sensitivity = _clamp01(getattr(p, "news_sensitivity", 0.5))
			risk_appetite_01 = _clamp01(((getattr(p, "risk_appetite", 0.0) + 1.0) / 2.0))
			rnd_ratio = _clamp01(getattr(c, "rnd_focus", 0.3))
			policy_dir_01 = _clamp01(((getattr(g, "policy_direction", 0.0) + 1.0) / 2.0))
			media_trust = _clamp01(getattr(media, "credibility", 0.7)) if media else 0.7
		else:
			news_sensitivity = _clamp01(p.get("news_sensitivity", 0.5))
			risk_appetite_01 = _clamp01(((float(p.get("risk_appetite", 0.0)) + 1.0) / 2.0))
			rnd_ratio = _clamp01(c.get("rnd_ratio", 0.3))
			policy_dir_01 = _clamp01(cast_to_float(g.get("policy_direction", 0.5)))
			media_trust = _clamp01(self.params.get("media", {}).get("trust", 0.7))

		return {
			"news_sensitivity": news_sensitivity,
			"risk_appetite": risk_appetite_01,
			"rnd_ratio": rnd_ratio,
			"policy_dir": policy_dir_01,
			"media_trust": media_trust,
		}

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

		vals = self._extract_values()
		news_sensitivity = vals["news_sensitivity"]
		risk_appetite = vals["risk_appetite"]
		rnd_ratio = vals["rnd_ratio"]
		policy_direction = vals["policy_dir"]
		media_trust = vals["media_trust"]

		# 1) 기본 가중치 계산 (엔티티/미디어 신뢰 반영)
		w_news = 0.35 + 0.2 * news_sensitivity + 0.05 * media_trust
		w_public = 0.25 + 0.15 * risk_appetite
		w_company = 0.2 + 0.2 * rnd_ratio
		w_gov = 0.2 + 0.2 * policy_direction

		# 2) 확장 지점: events_summary / external 반영 (옵션)
		if events_summary:
			surprise_ratio = _clamp01(events_summary.get("surprise_ratio", 0.0))
			pos_neg_ratio = _clamp01(events_summary.get("pos_neg_ratio", 0.5))
			w_news += 0.05 * surprise_ratio
			w_public += 0.05 * (pos_neg_ratio - 0.5)

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

# 보조: 안전한 float 변환

def cast_to_float(value, default=0.5) -> float:
	try:
		return float(value)
	except Exception:
		return float(default)
