from typing import Dict, List, Optional, Any


def _require(module_name: str):
	try:
		return __import__(module_name)
	except Exception as e:
		raise ImportError(f"'{module_name}' 패키지가 필요합니다. requirements.txt를 설치해주세요. 원인: {e}")


def build_sequence_from_prices(
	price_df,
	params_generator,
	external_df=None,
	price_col: str = "Close",
	date_col: str = "Date",
	media_trust: float = 0.8,
) -> List[Dict[str, Any]]:
	"""
	가격 데이터프레임과 간단한 파라미터 생성기를 이용해 학습용 시퀀스를 구성.
	- price_df: pandas DataFrame with columns [Date, Open, High, Low, Close, Volume]
	- params_generator: callable(date,row)->params dict (public/company/government 추정치)
	- external_df: 예: VIX 등의 외부지표 DataFrame (same date_col)
	- media_trust: 기본 미디어 신뢰도(0~1)
	"""
	pd = _require("pandas")
	
	df = price_df.copy()
	if date_col in df.columns:
		df[date_col] = pd.to_datetime(df[date_col])
		df = df.sort_values(by=date_col).reset_index(drop=True)
	
	if external_df is not None:
		ext = external_df.copy()
		if date_col in ext.columns:
			try:
				ext[date_col] = pd.to_datetime(ext[date_col])
			except Exception:
				pass
			df = pd.merge_asof(df, ext.sort_values(by=date_col), on=date_col)
	
	sequence: List[Dict[str, Any]] = []
	for _, row in df.iterrows():
		params = params_generator(row[date_col], row)
		# 간단한 이벤트 생성(뉴스 충격 대리): 당일 절대수익률을 proxy로 사용
		news_impact = 0.0
		try:
			prev_close = row.get("PrevClose")
			if prev_close is None and price_col in df.columns:
				# 이전 종가를 접근하기 위해 shift를 사용했어야 하지만, 여기선 builder 외부에서 처리하거나 0으로 둔다
				news_impact = 0.0
			else:
				news_impact = max(0.0, min(1.0, abs(float(row[price_col]) / float(prev_close) - 1.0)))
		except Exception:
			news_impact = 0.0
		
		seq_item = {
			"date": row[date_col],
			"price": float(row[price_col]),
			"params": params,
			"events": {"news_impact": news_impact, "media_credibility": media_trust},
		}
		sequence.append(seq_item)
	return sequence


def default_params_generator(date, row) -> Dict[str, Any]:
	"""
	가격만 있을 때 사용할 매우 단순한 기본 파라미터 생성기.
	- 변동성 대리: intraday range
	- risk_appetite: 최근 수익률 proxy(여기선 0으로 고정, 추후 EMA로 확장 가능)
	"""
	open_p = float(row.get("Open", row.get("open", 0.0)) or 0.0)
	close_p = float(row.get("Close", row.get("close", 0.0)) or 0.0)
	high_p = float(row.get("High", row.get("high", 0.0)) or 0.0)
	low_p = float(row.get("Low", row.get("low", 0.0)) or 0.0)
	intraday_range = 0.0
	try:
		if close_p > 0.0:
			intraday_range = (high_p - low_p) / close_p
	except Exception:
		intraday_range = 0.0
	
	company_trait = max(0.0, min(1.0, 0.5 + 0.5 * (intraday_range - 0.01)))
	params = {
		"public": {"risk_appetite": 0.0},
		"company": {"trait": company_trait},
		"government": {"policy_direction": 0.5},
	}
	return params 