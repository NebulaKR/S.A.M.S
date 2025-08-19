from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from utils.dataset import extract_basic_factors
from utils.simple_models import RidgeModel, vectorize_features


_MODEL_CACHE: Dict[str, RidgeModel] = {}


def load_ridge_model(model_path: str) -> RidgeModel:
	p = str(Path(model_path))
	if p in _MODEL_CACHE:
		return _MODEL_CACHE[p]
	with open(p, "r", encoding="utf-8") as f:
		data = json.load(f)
	model = RidgeModel.from_dict(data)
	_MODEL_CACHE[p] = model
	return model


def make_feature_vector(model: RidgeModel, params: Dict[str, Any], events: Optional[Dict[str, Any]] = None) -> List[List[float]]:
	features_dict = extract_basic_factors(params, events)
	feature_names = model.feature_names_ or list(features_dict.keys())
	X = vectorize_features([features_dict], feature_names)
	return X


def predict_delta_with_model(model_or_path: Any, params: Dict[str, Any], events: Optional[Dict[str, Any]] = None) -> float:
	if isinstance(model_or_path, (str, Path)):
		model = load_ridge_model(str(model_or_path))
	elif isinstance(model_or_path, RidgeModel):
		model = model_or_path
	else:
		raise ValueError("Unsupported model type. Pass a file path or RidgeModel instance.")
	X = make_feature_vector(model, params, events)
	pred = model.predict(X)[0]
	return float(pred)


def blend_deltas(rule_delta: float, ml_delta: float, weight_ml: float = 1.0) -> float:
	w = max(0.0, min(1.0, float(weight_ml)))
	return (1.0 - w) * float(rule_delta) + w * float(ml_delta) 