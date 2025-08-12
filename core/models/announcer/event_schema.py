from dataclasses import dataclass

@dataclass
class Event:
    event_type: str
    category: str
    sentiment: float  # -1.0 ~ +1.0
    impact_level: int  # 1~5
    duration: str      # 'short', 'mid', 'long'
    news_article: str
