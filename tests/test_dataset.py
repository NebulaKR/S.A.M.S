import unittest

from utils.dataset import build_supervised_from_sequence, build_labels_from_prices, extract_basic_factors


class TestDatasetLabeling(unittest.TestCase):
	def test_build_labels_from_prices(self):
		prices = [100, 101, 99, 99]
		labels_h1 = build_labels_from_prices(prices, horizon=1)
		self.assertAlmostEqual(labels_h1[0], (101/100)-1)
		self.assertAlmostEqual(labels_h1[1], (99/101)-1)
		self.assertAlmostEqual(labels_h1[2], (99/99)-1)
		self.assertIsNone(labels_h1[3])  # 마지막은 미래가 없어 None

	def test_build_supervised_alignment_no_leakage(self):
		sequence = [
			{"params": {"public": {"risk_appetite": 0.0}}, "events": {"news_impact": 0.2}, "price": 100.0},
			{"params": {"public": {"risk_appetite": 0.2}}, "events": {"news_impact": 0.1}, "price": 101.0},
			{"params": {"public": {"risk_appetite": -0.5}}, "events": {"news_impact": 0.0}, "price": 99.0},
		]
		X, y, pairs = build_supervised_from_sequence(sequence, horizon=1, label_key_future="realized_delta", allow_price_fallback=True)
		# 길이: n-h = 2, 마지막은 미래가 없어 제외
		self.assertEqual(len(X), 2)
		self.assertEqual(len(y), 2)
		self.assertEqual(pairs, [(0,1), (1,2)])
		# y는 (p_{t+1}/p_t)-1 로 계산되어야 함
		self.assertAlmostEqual(y[0], (101/100)-1)
		self.assertAlmostEqual(y[1], (99/101)-1)

	def test_extract_basic_factors_scale_consistency(self):
		params = {"public": {"risk_appetite": -1.0}, "company": {"orientation": 1.0}, "government": {"policy_direction": 0.0}}
		features = extract_basic_factors(params, {"news_impact": 1.2, "media_credibility": -0.5})
		# 스케일 클리핑 확인
		self.assertGreaterEqual(features["risk_appetite_01"], 0.0)
		self.assertLessEqual(features["risk_appetite_01"], 1.0)
		self.assertGreaterEqual(features["comp_trait_01"], 0.0)
		self.assertLessEqual(features["comp_trait_01"], 1.0)
		self.assertGreaterEqual(features["news_impact_01"], 0.0)
		self.assertLessEqual(features["news_impact_01"], 1.0)


if __name__ == "__main__":
	unittest.main() 