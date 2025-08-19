from typing import List, Dict, Any, Optional, Tuple
import math


class RidgeModel:
	def __init__(self):
		self.coef_: Optional[List[float]] = None
		self.intercept_: float = 0.0
		self.feature_names_: Optional[List[str]] = None
		self.mean_: Optional[List[float]] = None
		self.std_: Optional[List[float]] = None
		self.alpha_: float = 1e-3

	def _standardize(self, X: List[List[float]]) -> Tuple[List[List[float]], List[float], List[float]]:
		n = len(X)
		m = len(X[0]) if n > 0 else 0
		means = [0.0] * m
		stds = [0.0] * m
		# mean
		for j in range(m):
			s = 0.0
			for i in range(n):
				s += X[i][j]
			means[j] = s / max(1, n)
		# std (population std)
		for j in range(m):
			var = 0.0
			for i in range(n):
				d = X[i][j] - means[j]
				var += d * d
			var = var / max(1, n)
			stds[j] = math.sqrt(var) if var > 0 else 1.0
		# apply
		Xn = [[(X[i][j] - means[j]) / (stds[j] if stds[j] != 0 else 1.0) for j in range(m)] for i in range(n)]
		return Xn, means, stds

	def fit(self, X: List[List[float]], y: List[float], feature_names: List[str], alpha: float = 1e-3, standardize: bool = True):
		import numpy as np
		self.alpha_ = float(alpha)
		self.feature_names_ = list(feature_names)
		X_list = [list(map(float, row)) for row in X]
		y_arr = np.array(y, dtype=float)
		if standardize:
			Xn, means, stds = self._standardize(X_list)
			self.mean_ = means
			self.std_ = stds
			X_arr = np.array(Xn, dtype=float)
		else:
			self.mean_ = [0.0] * len(X_list[0])
			self.std_ = [1.0] * len(X_list[0])
			X_arr = np.array(X_list, dtype=float)
		# add bias column
		ones = np.ones((X_arr.shape[0], 1), dtype=float)
		Xb = np.concatenate([X_arr, ones], axis=1)
		# ridge closed-form: w = (X^T X + alpha I)^-1 X^T y
		m = Xb.shape[1]
		I = np.eye(m)
		I[-1, -1] = 0.0  # don't regularize bias
		A = Xb.T @ Xb + self.alpha_ * I
		b = Xb.T @ y_arr
		w = np.linalg.solve(A, b)
		self.coef_ = w[:-1].tolist()
		self.intercept_ = float(w[-1])
		return self

	def predict(self, X: List[List[float]]) -> List[float]:
		import numpy as np
		if self.coef_ is None or self.feature_names_ is None or self.mean_ is None or self.std_ is None:
			raise RuntimeError("Model is not fitted")
		X_list = [list(map(float, row)) for row in X]
		# standardize with stored params
		Xn = [[(X_list[i][j] - self.mean_[j]) / (self.std_[j] if self.std_[j] != 0 else 1.0) for j in range(len(self.coef_))] for i in range(len(X_list))]
		X_arr = np.array(Xn, dtype=float)
		pred = X_arr @ (np.array(self.coef_, dtype=float)) + self.intercept_
		return pred.tolist()

	def to_dict(self) -> Dict[str, Any]:
		return {
			"coef": self.coef_,
			"intercept": self.intercept_,
			"feature_names": self.feature_names_,
			"mean": self.mean_,
			"std": self.std_,
			"alpha": self.alpha_,
		}

	@staticmethod
	def from_dict(d: Dict[str, Any]) -> "RidgeModel":
		m = RidgeModel()
		m.coef_ = list(d["coef"]) if d.get("coef") is not None else None
		m.intercept_ = float(d.get("intercept", 0.0))
		m.feature_names_ = list(d.get("feature_names", []))
		m.mean_ = list(d.get("mean", []))
		m.std_ = list(d.get("std", []))
		m.alpha_ = float(d.get("alpha", 1e-3))
		return m


def vectorize_features(records: List[Dict[str, Any]], feature_names: List[str]) -> List[List[float]]:
	X: List[List[float]] = []
	for f in records:
		row = [float(f.get(name, 0.0)) for name in feature_names]
		X.append(row)
	return X


def metrics_regression(y_true: List[float], y_pred: List[float]) -> Dict[str, float]:
	import math
	n = len(y_true)
	rmse = math.sqrt(sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / max(1, n))
	mae = sum(abs(yt - yp) for yt, yp in zip(y_true, y_pred)) / max(1, n)
	dir_acc = sum((yt >= 0) == (yp >= 0) for yt, yp in zip(y_true, y_pred)) / max(1, n)
	return {"rmse": rmse, "mae": mae, "directional_accuracy": dir_acc} 