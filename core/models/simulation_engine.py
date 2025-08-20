import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from core.models.announcer.announcer import Announcer
from core.models.coach.coach import Coach
from core.models.main_model import main_model
from core.models.announcer.event import Event
from core.models.announcer.news import News


class SimulationSpeed(Enum):
    """시뮬레이션 속도 설정"""
    SLOW = 1      # 1초 = 1시간
    NORMAL = 2    # 1초 = 2시간  
    FAST = 5      # 1초 = 5시간
    ULTRA = 10    # 1초 = 10시간


class SimulationState(Enum):
    """시뮬레이션 상태"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class StockPrice:
    """주가 정보"""
    ticker: str
    base_price: float
    current_price: float
    change_rate: float
    volume: int
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SimulationEvent:
    """시뮬레이션 이벤트"""
    id: str
    event: Event
    timestamp: datetime
    affected_stocks: List[str]
    market_impact: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SimulationEngine:
    """SAMS 시뮬레이션 엔진"""
    
    def __init__(self, initial_data: Dict):
        """
        시뮬레이션 엔진 초기화
        
        Args:
            initial_data: 초기 시장 데이터
                {
                    "stocks": {
                        "005930": {"price": 79000, "volume": 1000000},
                        "000660": {"price": 45000, "volume": 500000}
                    },
                    "market_params": {
                        "public": {"risk_appetite": 0.3, "news_sensitivity": 0.7},
                        "government": {"policy_direction": 0.2},
                        "company": {"orientation": 0.1, "rnd_focus": 0.4}
                    }
                }
        """
        self.state = SimulationState.STOPPED
        self.speed = SimulationSpeed.NORMAL
        
        # 초기 데이터 설정
        self.stocks = initial_data.get("stocks", {})
        self.market_params = initial_data.get("market_params", {})
        
        # 시뮬레이션 시간 관리
        self.simulation_time = datetime.now()
        self.last_update = time.time()
        self.simulation_start_time = None
        
        # AI 모델들
        self.announcer = Announcer()
        self.coach = Coach(self.market_params)
        
        # 이벤트 및 뉴스 히스토리
        self.events_history: List[SimulationEvent] = []
        self.news_history: List[News] = []
        
        # 시뮬레이션 설정
        self.event_generation_interval = 300  # 5분마다 이벤트 생성
        self.last_event_generation = 0
        
        # 콜백 함수들
        self.on_price_change = None
        self.on_event_occur = None
        self.on_news_update = None
    
    def start(self):
        """시뮬레이션 시작"""
        if self.state == SimulationState.STOPPED:
            self.state = SimulationState.RUNNING
            self.simulation_start_time = datetime.now()
            self.simulation_time = self.simulation_start_time
            print(f"시뮬레이션 시작: {self.simulation_time}")
        elif self.state == SimulationState.PAUSED:
            self.state = SimulationState.RUNNING
            print("시뮬레이션 재개")
    
    def pause(self):
        """시뮬레이션 일시정지"""
        if self.state == SimulationState.RUNNING:
            self.state = SimulationState.PAUSED
            print("시뮬레이션 일시정지")
    
    def stop(self):
        """시뮬레이션 정지"""
        self.state = SimulationState.STOPPED
        print("시뮬레이션 정지")
    
    def set_speed(self, speed: SimulationSpeed):
        """시뮬레이션 속도 설정"""
        self.speed = speed
        print(f"시뮬레이션 속도 변경: {speed.name}")
    
    def update(self):
        """시뮬레이션 업데이트 (메인 루프에서 호출)"""
        if self.state != SimulationState.RUNNING:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        if time_diff < 1.0:  # 1초마다 업데이트
            return
        
        # 시뮬레이션 시간 진행
        hours_to_advance = time_diff * self.speed.value
        self.simulation_time += timedelta(hours=hours_to_advance)
        
        # 이벤트 생성 체크
        if current_time - self.last_event_generation >= self.event_generation_interval:
            self._generate_events()
            self.last_event_generation = current_time
        
        # 주가 업데이트
        self._update_stock_prices()
        
        self.last_update = current_time
    
    def _generate_events(self):
        """AI를 사용하여 새로운 이벤트 생성"""
        try:
            # 과거 이벤트들을 컨텍스트로 사용
            past_events = [event.event for event in self.events_history[-5:]] if self.events_history else []
            
            # 새로운 이벤트 생성
            new_events = self.announcer.generate_events(
                past_events=past_events,
                count=1,
                allowed_categories=["경제", "정책", "기업", "기술", "국제"]
            )
            
            for event in new_events:
                # 이벤트의 시장 영향도 계산
                market_impact = self._calculate_market_impact(event)
                
                # 영향받는 주식들 결정
                affected_stocks = self._determine_affected_stocks(event)
                
                # 시뮬레이션 이벤트 생성
                sim_event = SimulationEvent(
                    id=event.id,
                    event=event,
                    timestamp=self.simulation_time,
                    affected_stocks=affected_stocks,
                    market_impact=market_impact
                )
                
                self.events_history.append(sim_event)
                
                # 콜백 호출
                if self.on_event_occur:
                    self.on_event_occur(sim_event)
                
                print(f"[{self.simulation_time.strftime('%Y-%m-%d %H:%M')}] "
                      f"새로운 이벤트: {event.event_type} (영향도: {market_impact:.3f})")
                
        except Exception as e:
            print(f"이벤트 생성 중 오류: {e}")
    
    def _calculate_market_impact(self, event: Event) -> float:
        """이벤트의 시장 영향도 계산"""
        # 감정 점수와 영향 레벨을 기반으로 영향도 계산
        sentiment_factor = (event.sentiment + 1) / 2  # -1~1을 0~1로 변환
        impact_factor = event.impact_level / 5.0  # 1~5를 0~1로 변환
        
        # 기본 영향도
        base_impact = sentiment_factor * impact_factor
        
        # 랜덤성 추가 (실제 시장의 불확실성 반영)
        import random
        random_factor = random.uniform(0.8, 1.2)
        
        return base_impact * random_factor
    
    def _determine_affected_stocks(self, event: Event) -> List[str]:
        """이벤트가 영향을 미치는 주식들 결정"""
        # 섹터별 영향 종목 매핑
        sector_mapping = {
            # 반도체/전자
            "반도체": ["005930", "000660", "011070"],  # 삼성전자, SK하이닉스, LG이노텍
            "전자": ["005930", "000660", "011070"],
            
            # 자동차/조선
            "자동차": ["005380", "005490"],  # 현대차, 기아
            "조선": ["009540", "010140"],  # 현대중공업, 삼성중공업
            "방산": ["012450"],  # 한화에어로스페이스
            
            # 화학/에너지
            "화학": ["051910", "006400", "373220"],  # LG화학, 삼성SDI, LG에너지솔루션
            "에너지": ["096770", "015760"],  # SK이노베이션, 한국전력
            
            # 금융
            "금융": ["055550", "086790", "105560", "138930", "323410"],  # 신한, 하나, KB, BNK, 카카오뱅크
            "은행": ["055550", "086790", "105560", "138930", "323410"],
            
            # 건설
            "건설": ["028260"],  # 삼성물산
            
            # 통신/미디어
            "통신": ["017670", "030200"],  # SK텔레콤, KT
            "인터넷": ["035420", "035720"],  # NAVER, 카카오
            "미디어": ["035420", "035720"],
            
            # 바이오/제약
            "바이오": ["068270", "207940"],  # 셀트리온, 삼성바이오로직스
            "제약": ["068270", "207940"],
            
            # 소비재
            "식품": ["097950"],  # CJ제일제당
            "소비재": ["097950"],
            
            # 기술
            "기술": ["005930", "000660", "035420", "035720"],  # 대표 기술주들
            "AI": ["005930", "000660", "035420", "035720"],  # AI 관련주
            "디지털": ["035420", "035720", "323410"],  # 디지털 전환 관련주
        }
        
        # 카테고리별 영향 종목 결정
        affected = []
        
        # 섹터 매핑 확인
        for sector, stocks in sector_mapping.items():
            if sector in event.category or sector in event.event_type:
                affected.extend(stocks)
        
        # 키워드별 영향 종목 결정
        keywords = {
            "금리": ["055550", "086790", "105560", "138930"],  # 금융주
            "환율": ["005380", "005490", "009540", "010140"],  # 수출주
            "원자재": ["051910", "006400", "373220", "096770"],  # 원자재 수혜주
            "정책": ["015760", "096770", "051910"],  # 정책 수혜주
            "경기": ["005380", "005490", "028260", "009540"],  # 경기 민감주
            "방산": ["012450", "009540", "010140"],  # 방산주
            "친환경": ["006400", "373220", "005380", "005490"],  # 친환경 관련주
            "디지털": ["035420", "035720", "323410"],  # 디지털 전환주
        }
        
        for keyword, stocks in keywords.items():
            if keyword in event.event_type or keyword in event.category:
                affected.extend(stocks)
        
        # 중복 제거
        affected = list(set(affected))
        
        # 이벤트가 너무 광범위한 경우 전체 시장에 영향
        if len(affected) == 0 or event.impact_level >= 4:
            affected = list(self.stocks.keys())
        
        return affected
    
    def _update_stock_prices(self):
        """주가 업데이트"""
        for ticker, stock_data in self.stocks.items():
            # 최근 이벤트들의 영향을 종합
            recent_events = [e for e in self.events_history 
                           if ticker in e.affected_stocks and 
                           (self.simulation_time - e.timestamp).total_seconds() < 3600]  # 1시간 내 이벤트
            
            if recent_events:
                # 이벤트들의 종합 영향도 계산
                total_impact = sum(e.market_impact for e in recent_events)
                
                # 코치 모델을 통한 가중치 조정
                weights = self.coach.adjust_weights()
                
                # 메인 모델을 통한 주가 변화 계산
                event_data = {
                    "news_impact": total_impact,
                    "media_credibility": 0.8
                }
                
                result = main_model(
                    weights=weights,
                    params=self.market_params,
                    events=event_data,
                    base_price=stock_data["price"]
                )
                
                # 주가 업데이트
                old_price = stock_data["price"]
                new_price = result["price"]
                change_rate = result["delta"]
                
                stock_data["price"] = new_price
                stock_data["change_rate"] = change_rate
                
                # 콜백 호출
                if self.on_price_change:
                    stock_price = StockPrice(
                        ticker=ticker,
                        base_price=old_price,
                        current_price=new_price,
                        change_rate=change_rate,
                        volume=stock_data.get("volume", 0),
                        timestamp=self.simulation_time
                    )
                    self.on_price_change(stock_price)
    
    def get_current_state(self) -> Dict:
        """현재 시뮬레이션 상태 반환"""
        return {
            "state": self.state.value,
            "speed": self.speed.value,
            "simulation_time": self.simulation_time.isoformat(),
            "stocks": self.stocks,
            "recent_events": [e.to_dict() for e in self.events_history[-5:]],
            "recent_news": [n.to_dict() for n in self.news_history[-5:]]
        }
    
    def get_stock_price(self, ticker: str) -> Optional[StockPrice]:
        """특정 주식의 현재 가격 정보 반환"""
        if ticker not in self.stocks:
            return None
        
        stock_data = self.stocks[ticker]
        return StockPrice(
            ticker=ticker,
            base_price=stock_data.get("base_price", stock_data["price"]),
            current_price=stock_data["price"],
            change_rate=stock_data.get("change_rate", 0.0),
            volume=stock_data.get("volume", 0),
            timestamp=self.simulation_time
        )
    
    def add_callback(self, event_type: str, callback):
        """콜백 함수 등록"""
        if event_type == "price_change":
            self.on_price_change = callback
        elif event_type == "event_occur":
            self.on_event_occur = callback
        elif event_type == "news_update":
            self.on_news_update = callback 