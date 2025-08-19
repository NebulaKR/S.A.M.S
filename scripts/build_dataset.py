#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys
import os

# Ensure project root (parent of scripts/) is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from utils.data_sources import download_ohlc
from utils.dataset_builder import build_sequence_from_prices, default_params_generator
from utils.dataset import build_supervised_from_sequence


def normalize_ticker_for_source(ticker: str, source: str) -> str:
	# FDR은 한국 종목에서 접미사 .KS/.KQ 없이 숫자 코드 사용, 지수는 KS11/KQ11 등
	if source == "fdr":
		if ticker.endswith(".KS") or ticker.endswith(".KQ"):
			return ticker.split(".")[0]
		if ticker.startswith("^"):
			return ticker[1:]
	return ticker


def main():
	parser = argparse.ArgumentParser(description="시뮬레이션 학습용 데이터셋 빌더")
	parser.add_argument("--ticker", type=str, default="AAPL", help="티커 (Yahoo 또는 FDR)")
	parser.add_argument("--start", type=str, default="2020-01-01")
	parser.add_argument("--end", type=str, default=None)
	parser.add_argument("--horizon", type=int, default=1)
	parser.add_argument("--source", type=str, default="auto", choices=["auto", "yahoo", "fdr"])
	parser.add_argument("--out", type=str, default="data/dataset.jsonl")
	args = parser.parse_args()

	ticker = normalize_ticker_for_source(args.ticker, args.source)
	price_df = download_ohlc(ticker, start=args.start, end=args.end, source=args.source)
	# 이전 종가 컬럼 준비(뉴스 임팩트 proxy용)
	try:
		import pandas as pd
		price_df = price_df.sort_values(by="Date").reset_index(drop=True)
		price_df["PrevClose"] = price_df["Close"].shift(1)
	except Exception:
		pass

	sequence = build_sequence_from_prices(price_df, default_params_generator)
	X, y, pairs = build_supervised_from_sequence(sequence, horizon=args.horizon, allow_price_fallback=True)

	out_path = Path(args.out)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open("w", encoding="utf-8") as f:
		for i, (features, label, (t0, t1)) in enumerate(zip(X, y, pairs)):
			rec = {
				"features": features,
				"label": label,
				"t_pair": [int(t0), int(t1)],
			}
			f.write(json.dumps(rec, ensure_ascii=False) + "\n")

	print(f"saved: {out_path} (n={len(X)})")


if __name__ == "__main__":
	main() 