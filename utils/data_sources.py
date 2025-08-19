from typing import Optional


def _require(module_name: str):
	try:
		return __import__(module_name)
	except Exception as e:
		raise ImportError(f"'{module_name}' 패키지가 필요합니다. requirements.txt를 설치해주세요. 원인: {e}")


def download_ohlc_yahoo(ticker: str, start: Optional[str] = None, end: Optional[str] = None, interval: str = "1d"):
	yf = _require("yfinance")
	pd = _require("pandas")
	data = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
	if data is None or len(data) == 0:
		raise ValueError(f"데이터가 비어있습니다: {ticker}")
	cols = {c: c.capitalize() for c in data.columns}
	data = data.rename(columns=cols)
	data = data.reset_index()
	return data


def download_ohlc_fdr(ticker: str, start: Optional[str] = None, end: Optional[str] = None):
	fdr = _require("FinanceDataReader")
	pd = _require("pandas")
	# FDR는 KRX의 경우 '005930'처럼 접미사 없이 사용, 지수는 'KS11'
	df = fdr.DataReader(ticker, start, end)
	if df is None or len(df) == 0:
		raise ValueError(f"데이터가 비어있습니다(FDR): {ticker}")
	# 인덱스를 컬럼으로 변환
	df = df.reset_index()
	# 이미 Open/High/Low/Close/Volume 표준 컬럼 사용
	return df


def download_ohlc(ticker: str, start: Optional[str] = None, end: Optional[str] = None, interval: str = "1d", source: str = "auto"):
	"""
	OHLC 데이터 다운로드. source 옵션:
	- 'yahoo': yfinance 사용 (예: 'AAPL', '005930.KS', '^KS11')
	- 'fdr': FinanceDataReader 사용 (예: '005930', 'KS11')
	- 'auto': yahoo 시도 후 실패 시 fdr로 폴백
	"""
	last_err = None
	if source in ("yahoo", "auto"):
		try:
			return download_ohlc_yahoo(ticker, start=start, end=end, interval=interval)
		except Exception as e:
			last_err = e
			if source == "yahoo":
				raise
	# fdr 경로 (KR 전용)
	if source in ("fdr", "auto"):
		try:
			return download_ohlc_fdr(ticker, start=start, end=end)
		except Exception as e:
			last_err = e
	# 모두 실패
	raise ValueError(f"OHLC 다운로드 실패: {ticker}. 마지막 오류: {last_err}") 