from typing import Any, Dict, List, Optional
import random

from .coach.coach import Coach


class InvestorBot:
    """투자자나 그룹 구성원을 나타내는 가벼운 트레이딩 에이전트입니다.

    봇은 주문 생성에 영향을 미치는 작은 전략 파라미터 세트를 유지합니다.
    상위 레벨의 코치가 이러한 파라미터를 주기적으로 조정하는 역할을 합니다.
    """

    def __init__(self, bot_id: str, capital: float, params: Optional[Dict[str, float]] = None):
        self.bot_id = bot_id
        self.capital = capital
        # 전략 파라미터는 [0,1] 범위; 의미는 애플리케이션에 따라 정의됩니다
        self.params: Dict[str, float] = params.copy() if params else {}
        self.positions: Dict[str, float] = {}

    def update_params(self, new_weights: Dict[str, float]) -> None:
        """코치의 가중치 조정 값을 적용합니다.

        정규화된 가중치에서 전략 파라미터로의 매핑은 시뮬레이션에
        따라 달라질 수 있습니다. 기본적으로는 중복되는 키에 대해
        값을 그대로 복사합니다. 추가 로직은 외부에서 구현 가능합니다.
        """
        for k, v in new_weights.items():
            self.params[k] = v

    def decide_orders(self, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """내부 상태를 바탕으로 주문 목록을 반환합니다.

        데모 목적상 이 메서드는 임의의 지정가 주문을 생성합니다.
        실제 구현에서는 가격, 뉴스, 내부 파라미터 등을 살펴 의미있는
        주문을 구성할 것입니다.
        """
        ticker = market_state.get("ticker", "TEST")
        price = market_state.get("price", 100.0)
        side = "buy" if random.random() < 0.5 else "sell"
        qty = round(random.random() * 10, 2)
        return [{
            "bot_id": self.bot_id,
            "ticker": ticker,
            "side": side,
            "price": price * (1 + (random.random() - 0.5) * 0.01),
            "quantity": qty,
        }]

    def __repr__(self):
        return f"<InvestorBot {self.bot_id} cap={self.capital} params={self.params}>"


class BotGroup:
    """코치가 관리하는 봇들의 묶음입니다.

    그룹은 하나 이상의 봇과 Coach 인스턴스를 연결하여
    코치가 거시적 요인에 따라 그룹 전체의 파라미터를
    주기적으로 조정할 수 있도록 합니다.
    """

    def __init__(
        self,
        group_id: str,
        coach: Coach,
        bots: Optional[List[InvestorBot]] = None, 
    ):
        self.group_id = group_id
        self.coach = coach
        self.bots: List[InvestorBot] = bots if bots else []

    def add_bot(self, bot: InvestorBot) -> None:
        self.bots.append(bot)

    def update_group_strategy(
        self,
        events_summary: Optional[Dict] = None,
        external: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """코치에게 새로운 가중치를 요청하고 모든 봇에 전달합니다.

        로깅을 위해 계산된 가중치 딕셔너리를 반환합니다.
        """
        weights = self.coach.adjust_weights(events_summary, external)
        for bot in self.bots:
            bot.update_params(weights)
        return weights

    def collect_orders(self, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        orders: List[Dict[str, Any]] = []
        for bot in self.bots:
            orders.extend(bot.decide_orders(market_state))
        return orders

    def __repr__(self):
        return f"<BotGroup {self.group_id} bots={len(self.bots)}>"
