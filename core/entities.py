class News:
    def __init__(self, bias: float, credibility: float, impact_level: int, category: str, sentiment: float):
        self.bias = bias                  # -1 ~ +1
        self.credibility = credibility    # 0 ~ 1
        self.impact_level = impact_level  # 1 ~ 5
        self.category = category          # e.g., "IT", "사회", ...
        self.sentiment = sentiment        # -1 ~ +1

class Public:
    def __init__(self, consumer_index: float, risk_appetite: float, news_sensitivity: float):
        self.consumer_index = consumer_index      # 0 ~ 100
        self.risk_appetite = risk_appetite        # -1 ~ +1
        self.news_sensitivity = news_sensitivity  # 0 ~ 1

class Company:
    def __init__(self, industry: str, orientation: float, size: str, rnd_focus: float, volatility: float):
        self.industry = industry              # e.g., "IT", "식품"
        self.orientation = orientation        # -1 ~ +1 (보수적~혁신적)
        self.size = size                      # "대기업", "중견", "스타트업"
        self.rnd_focus = rnd_focus            # 0 ~ 1
        self.volatility = volatility          # 0 ~ 1

class Government:
    def __init__(self, policy_direction: float, interest_rate: float, tax_policy: float, industry_support: dict):
        self.policy_direction = policy_direction          # -1 ~ +1
        self.interest_rate = interest_rate                # float (%)
        self.tax_policy = tax_policy                      # -1(증세) ~ +1(감세)
        self.industry_support = industry_support or {}    # 예: {'IT': +0.3, '식품': 0}
