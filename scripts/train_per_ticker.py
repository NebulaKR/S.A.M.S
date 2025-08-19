#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys
import os

# Ensure project root is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from utils.simple_models import RidgeModel, vectorize_features, metrics_regression


def load_jsonl(path: str):
	records = []
	with open(path, "r", encoding="utf-8") as f:
		for line in f:
			obj = json.loads(line)
			records.append(obj)
	return records


def expanding_window_cv(records, feature_names, min_train=252, step=21):
	"""
	연도별이 아닌 시계열 확장형 CV. min_train 거래일(약 1년)부터 시작, step 간격으로 확장하며 검증.
	"""
	n = len(records)
	folds = []
	for split in range(min_train, n - step, step):
		train = records[:split]
		valid = records[split: split + step]
		folds.append((train, valid))
	return folds


def prepare_xy(records, feature_names):
	X = vectorize_features([r["features"] for r in records], feature_names)
	y = [float(r["label"]) for r in records]
	return X, y


def train_one_ticker(dataset_path: str, alpha: float = 1e-3, min_train: int = 252, step: int = 21):
	records = load_jsonl(dataset_path)
	feature_names = list(records[0]["features"].keys())
	folds = expanding_window_cv(records, feature_names, min_train=min_train, step=step)

	metrics_all = []
	for train_recs, valid_recs in folds:
		X_tr, y_tr = prepare_xy(train_recs, feature_names)
		X_va, y_va = prepare_xy(valid_recs, feature_names)
		model = RidgeModel().fit(X_tr, y_tr, feature_names, alpha=alpha, standardize=True)
		preds = model.predict(X_va)
		metrics = metrics_regression(y_va, preds)
		metrics_all.append(metrics)

	# 마지막 전체 학습으로 최종 모델 저장용
	X_full, y_full = prepare_xy(records, feature_names)
	final_model = RidgeModel().fit(X_full, y_full, feature_names, alpha=alpha, standardize=True)
	return final_model, metrics_all


def main():
	parser = argparse.ArgumentParser(description="티커별 Ridge 회귀 학습 (Expanding CV)")
	parser.add_argument("--in", dest="in_path", type=str, required=True)
	parser.add_argument("--alpha", type=float, default=1e-3)
	parser.add_argument("--min-train", type=int, default=252)
	parser.add_argument("--step", type=int, default=21)
	parser.add_argument("--out-model", type=str, default=None)
	args = parser.parse_args()

	model, metrics_all = train_one_ticker(args.in_path, alpha=args.alpha, min_train=args.min_train, step=args.step)
	avg = {k: sum(d[k] for d in metrics_all) / len(metrics_all) for k in metrics_all[0].keys()} if metrics_all else {}
	print("CV avg:", avg)

	if args.out_model:
		out_path = Path(args.out_model)
		out_path.parent.mkdir(parents=True, exist_ok=True)
		with out_path.open("w", encoding="utf-8") as f:
			f.write(json.dumps(model.to_dict(), ensure_ascii=False))
		print(f"saved model: {out_path}")


if __name__ == "__main__":
	main() 