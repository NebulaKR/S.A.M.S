import unittest

from core.models.coach.coach import Coach


class TestCoach(unittest.TestCase):
    def setUp(self):
        self.params = {
            "public": {"news_sensitivity": 0.6, "risk_appetite": 0.2},
            "company": {"rnd_ratio": 0.3},
            "government": {"policy_direction": 0.4},
        }

    def test_weights_clamped_and_normalized(self):
        coach = Coach(self.params)
        weights = coach.adjust_weights()
        # [0,1] 범위
        for v in weights.values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)
        # 합=1 정규화
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)

    def test_events_summary_affects_weights(self):
        coach = Coach(self.params)
        w_base = coach.adjust_weights()
        w_surprise = coach.adjust_weights(events_summary={"surprise_ratio": 1.0})
        self.assertGreaterEqual(w_surprise["w_news"], w_base["w_news"])  # 놀람이 크면 뉴스 비중↑

    def test_external_vix_affects_news_weight(self):
        coach = Coach(self.params)
        w_low_vix = coach.adjust_weights(external={"vix": 0.0})
        w_high_vix = coach.adjust_weights(external={"vix": 1.0})
        self.assertGreaterEqual(w_high_vix["w_news"], w_low_vix["w_news"])  # VIX↑ → 뉴스 비중↑


if __name__ == "__main__":
    unittest.main() 