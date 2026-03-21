import sys
import os
from pathlib import Path

# ensure project root is on path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.models.agents import InvestorBot, BotGroup
from core.models.coach.coach import Coach


def test_bot_parameter_update():
    coach = Coach({
        "public": {"news_sensitivity": 0.2, "risk_appetite": -0.5},
        "company": {"rnd_ratio": 0.1},
        "government": {"policy_direction": 0.0},
    })
    group = BotGroup("grp1", coach)
    b1 = InvestorBot("bot1", capital=1000.0)
    b2 = InvestorBot("bot2", capital=500.0)
    group.add_bot(b1)
    group.add_bot(b2)

    weights = group.update_group_strategy()
    assert all(0.0 <= v <= 1.0 for v in weights.values())
    # each bot should have received the same weights
    assert b1.params == b2.params == weights


def test_collect_orders_returns_orders():
    coach = Coach({})
    group = BotGroup("grp2", coach, bots=[InvestorBot("botA", 100)])
    market = {"ticker": "TEST", "price": 50.0}
    orders = group.collect_orders(market)
    assert isinstance(orders, list)
    assert orders and isinstance(orders[0], dict)
    assert orders[0]["ticker"] == "TEST"


if __name__ == "__main__":
    # simple runner compatible with existing test suite
    print("Running agent module tests...")
    test_bot_parameter_update()
    test_collect_orders_returns_orders()
    print("All agent tests passed")
