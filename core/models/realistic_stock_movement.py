"""
현실적인 주가 변동 모델
과거 데이터 기반 학습, 섹터별 차별화, 기업별 특성 반영
"""

import random
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class RealisticStockMovement:
    """현실적인 주가 변동을 계산하는 모델"""
    
    def __init__(self, data_dir: str = "data/kr"):
        self.data_dir = data_dir
        self.stock_characteristics = self._load_stock_characteristics()
        self.sector_relationships = self._load_sector_relationships()
        self.price_history = self._load_price_history()
        self.volatility_patterns = self._analyze_volatility_patterns()
        self.historical_volatility = self._load_historical_volatility()
        
    def _load_price_history(self) -> Dict[str, List[float]]:
        """실제 주가 데이터 로드"""
        price_history = {}
        
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.jsonl') and filename != 'KS11_h1.jsonl':
                    ticker = filename.split('_')[0]
                    filepath = os.path.join(self.data_dir, filename)
                    
                    prices = []
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line.strip())
                                # label이 주가 변동률 (예: 0.011760094080752737 = 1.18%)
                                if 'label' in data:
                                    prices.append(data['label'])
                            except json.JSONDecodeError:
                                continue
                    
                    if prices:
                        price_history[ticker] = prices
                        print(f"[DATA] {ticker}: {len(prices)}개 데이터 포인트 로드")
        
        except Exception as e:
            print(f"[WARNING] 실제 데이터 로드 실패: {e}")
        
        return price_history
    
    def _analyze_volatility_patterns(self) -> Dict[str, Dict]:
        """실제 데이터 기반 변동성 패턴 분석"""
        patterns = {}
        
        for ticker, prices in self.price_history.items():
            if len(prices) < 10:  # 최소 데이터 포인트 필요
                continue
                
            prices_array = np.array(prices)
            
            # 기본 통계
            mean_change = np.mean(prices_array)
            std_change = np.std(prices_array)
            max_change = np.max(np.abs(prices_array))
            
            # 변동성 패턴 (연속된 변화의 상관관계)
            if len(prices_array) > 1:
                correlation = np.corrcoef(prices_array[:-1], prices_array[1:])[0, 1]
            else:
                correlation = 0.0
            
            # 극단적 변동 빈도 (2% 이상)
            extreme_changes = np.sum(np.abs(prices_array) > 0.02)
            extreme_ratio = extreme_changes / len(prices_array)
            
            # 연속 상승/하락 패턴
            consecutive_up = 0
            consecutive_down = 0
            max_consecutive_up = 0
            max_consecutive_down = 0
            
            current_up = 0
            current_down = 0
            
            for change in prices_array:
                if change > 0:
                    current_up += 1
                    current_down = 0
                    max_consecutive_up = max(max_consecutive_up, current_up)
                elif change < 0:
                    current_down += 1
                    current_up = 0
                    max_consecutive_down = max(max_consecutive_down, current_down)
            
            patterns[ticker] = {
                'mean_change': mean_change,
                'std_change': std_change,
                'max_change': max_change,
                'correlation': correlation,
                'extreme_ratio': extreme_ratio,
                'max_consecutive_up': max_consecutive_up,
                'max_consecutive_down': max_consecutive_down,
                'data_points': len(prices_array)
            }
            
            print(f"[ANALYSIS] {ticker}: 평균변동 {mean_change:.4f}, 표준편차 {std_change:.4f}, 극단비율 {extreme_ratio:.3f}")
        
        return patterns
    
    def _load_stock_characteristics(self) -> Dict[str, Dict]:
        """주식별 특성 로드"""
        return {
            '005930': {  # 삼성전자
                'name': '삼성전자',
                'sector': 'IT/전자',
                'market_cap': 'large',  # 대형주
                'volatility': 0.85,     # 변동성 (0.5~1.0)
                'news_sensitivity': 0.9, # 뉴스 민감도
                'sector_weight': 0.25,   # 섹터 내 비중
                'base_volume': 1000000   # 기본 거래량
            },
            '000660': {  # SK하이닉스
                'name': 'SK하이닉스',
                'sector': 'IT/전자',
                'market_cap': 'large',
                'volatility': 0.9,
                'news_sensitivity': 0.95,
                'sector_weight': 0.2,
                'base_volume': 800000
            },
            '005380': {  # 현대차
                'name': '현대차',
                'sector': '자동차',
                'market_cap': 'large',
                'volatility': 0.7,
                'news_sensitivity': 0.8,
                'sector_weight': 0.3,
                'base_volume': 600000
            },
            '005490': {  # 포스코홀딩스
                'name': '포스코홀딩스',
                'sector': '철강/소재',
                'market_cap': 'large',
                'volatility': 0.75,
                'news_sensitivity': 0.7,
                'sector_weight': 0.25,
                'base_volume': 400000
            },
            '051910': {  # LG화학
                'name': 'LG화학',
                'sector': '화학',
                'market_cap': 'large',
                'volatility': 0.8,
                'news_sensitivity': 0.85,
                'sector_weight': 0.2,
                'base_volume': 300000
            },
            '097950': {  # CJ대한통운
                'name': 'CJ대한통운',
                'sector': '물류/운송',
                'market_cap': 'medium',
                'volatility': 0.6,
                'news_sensitivity': 0.6,
                'sector_weight': 0.15,
                'base_volume': 200000
            },
            '006400': {  # 삼성SDI
                'name': '삼성SDI',
                'sector': 'IT/전자',
                'market_cap': 'medium',
                'volatility': 0.8,
                'news_sensitivity': 0.85,
                'sector_weight': 0.1,
                'base_volume': 250000
            },
            '373220': {  # LG에너지솔루션
                'name': 'LG에너지솔루션',
                'sector': 'IT/전자',
                'market_cap': 'medium',
                'volatility': 0.85,
                'news_sensitivity': 0.9,
                'sector_weight': 0.1,
                'base_volume': 300000
            },
            '096770': {  # SK이노베이션
                'name': 'SK이노베이션',
                'sector': '에너지',
                'market_cap': 'medium',
                'volatility': 0.7,
                'news_sensitivity': 0.75,
                'sector_weight': 0.2,
                'base_volume': 180000
            },
            '055550': {  # 신한지주
                'name': '신한지주',
                'sector': '금융',
                'market_cap': 'large',
                'volatility': 0.6,
                'news_sensitivity': 0.7,
                'sector_weight': 0.2,
                'base_volume': 500000
            },
            '086790': {  # 하나금융지주
                'name': '하나금융지주',
                'sector': '금융',
                'market_cap': 'large',
                'volatility': 0.6,
                'news_sensitivity': 0.7,
                'sector_weight': 0.15,
                'base_volume': 400000
            },
            '105560': {  # KB금융지주
                'name': 'KB금융지주',
                'sector': '금융',
                'market_cap': 'large',
                'volatility': 0.6,
                'news_sensitivity': 0.7,
                'sector_weight': 0.2,
                'base_volume': 450000
            },
            '138930': {  # BNK금융지주
                'name': 'BNK금융지주',
                'sector': '금융',
                'market_cap': 'medium',
                'volatility': 0.65,
                'news_sensitivity': 0.65,
                'sector_weight': 0.05,
                'base_volume': 100000
            },
            '323410': {  # 카카오뱅크
                'name': '카카오뱅크',
                'sector': '금융',
                'market_cap': 'medium',
                'volatility': 0.8,
                'news_sensitivity': 0.85,
                'sector_weight': 0.1,
                'base_volume': 150000
            },
            '028260': {  # 삼성물산
                'name': '삼성물산',
                'sector': '건설',
                'market_cap': 'medium',
                'volatility': 0.7,
                'news_sensitivity': 0.6,
                'sector_weight': 0.15,
                'base_volume': 120000
            },
            '009540': {  # 한샘
                'name': '한샘',
                'sector': '소비재',
                'market_cap': 'medium',
                'volatility': 0.65,
                'news_sensitivity': 0.6,
                'sector_weight': 0.1,
                'base_volume': 80000
            },
            '010140': {  # 삼성전기
                'name': '삼성전기',
                'sector': 'IT/전자',
                'market_cap': 'medium',
                'volatility': 0.75,
                'news_sensitivity': 0.8,
                'sector_weight': 0.08,
                'base_volume': 200000
            },
            '017670': {  # SK텔레콤
                'name': 'SK텔레콤',
                'sector': '통신',
                'market_cap': 'large',
                'volatility': 0.6,
                'news_sensitivity': 0.7,
                'sector_weight': 0.25,
                'base_volume': 350000
            },
            '030200': {  # KT
                'name': 'KT',
                'sector': '통신',
                'market_cap': 'large',
                'volatility': 0.6,
                'news_sensitivity': 0.7,
                'sector_weight': 0.2,
                'base_volume': 300000
            },
            '015760': {  # 한국전력
                'name': '한국전력',
                'sector': '에너지',
                'market_cap': 'large',
                'volatility': 0.5,
                'news_sensitivity': 0.6,
                'sector_weight': 0.3,
                'base_volume': 400000
            },
            '068270': {  # 셀트리온
                'name': '셀트리온',
                'sector': '바이오',
                'market_cap': 'large',
                'volatility': 0.9,
                'news_sensitivity': 0.95,
                'sector_weight': 0.25,
                'base_volume': 250000
            },
            '207940': {  # 삼성바이오로직스
                'name': '삼성바이오로직스',
                'sector': '바이오',
                'market_cap': 'large',
                'volatility': 0.9,
                'news_sensitivity': 0.95,
                'sector_weight': 0.2,
                'base_volume': 200000
            }
        }
    
    def _load_sector_relationships(self) -> Dict[str, Dict[str, float]]:
        """섹터 간 연관성 로드"""
        return {
            'IT/전자': {
                'IT/전자': 1.0,      # 동일 섹터
                '바이오': 0.3,        # 약한 양의 상관관계
                '화학': 0.2,          # 약한 양의 상관관계
                '자동차': 0.1,        # 약한 양의 상관관계
                '금융': 0.0,          # 무관
                '건설': -0.1,         # 약한 음의 상관관계
                '에너지': 0.0,        # 무관
                '소비재': 0.0,        # 무관
                '통신': 0.2,          # 약한 양의 상관관계
                '물류/운송': 0.0      # 무관
            },
            '자동차': {
                'IT/전자': 0.1,
                '바이오': 0.0,
                '화학': 0.3,          # 배터리 관련
                '자동차': 1.0,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.2,        # 전기차 관련
                '소비재': 0.1,
                '통신': 0.0,
                '물류/운송': 0.1
            },
            '바이오': {
                'IT/전자': 0.3,
                '바이오': 1.0,
                '화학': 0.4,          # 약품 관련
                '자동차': 0.0,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.0,
                '소비재': 0.0,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '화학': {
                'IT/전자': 0.2,
                '바이오': 0.4,
                '화학': 1.0,
                '자동차': 0.3,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.3,
                '소비재': 0.1,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '금융': {
                'IT/전자': 0.0,
                '바이오': 0.0,
                '화학': 0.0,
                '자동차': 0.0,
                '금융': 1.0,
                '건설': 0.0,
                '에너지': 0.0,
                '소비재': 0.0,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '건설': {
                'IT/전자': -0.1,
                '바이오': 0.0,
                '화학': 0.0,
                '자동차': 0.0,
                '금융': 0.0,
                '건설': 1.0,
                '에너지': 0.0,
                '소비재': 0.0,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '에너지': {
                'IT/전자': 0.0,
                '바이오': 0.0,
                '화학': 0.3,
                '자동차': 0.2,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 1.0,
                '소비재': 0.0,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '소비재': {
                'IT/전자': 0.0,
                '바이오': 0.0,
                '화학': 0.1,
                '자동차': 0.1,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.0,
                '소비재': 1.0,
                '통신': 0.0,
                '물류/운송': 0.0
            },
            '통신': {
                'IT/전자': 0.2,
                '바이오': 0.0,
                '화학': 0.0,
                '자동차': 0.0,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.0,
                '소비재': 0.0,
                '통신': 1.0,
                '물류/운송': 0.0
            },
            '물류/운송': {
                'IT/전자': 0.0,
                '바이오': 0.0,
                '화학': 0.0,
                '자동차': 0.1,
                '금융': 0.0,
                '건설': 0.0,
                '에너지': 0.0,
                '소비재': 0.0,
                '통신': 0.0,
                '물류/운송': 1.0
            }
        }
    
    def _load_historical_volatility(self) -> Dict[str, float]:
        """과거 데이터 기반 변동성 로드"""
        # 실제 데이터가 있으면 그것을 사용, 없으면 기본값 사용
        if self.volatility_patterns:
            volatility = {}
            for ticker, pattern in self.volatility_patterns.items():
                # 실제 데이터의 표준편차를 기반으로 변동성 계산
                # 표준편차가 클수록 변동성이 큼
                std_change = pattern['std_change']
                volatility[ticker] = min(0.95, max(0.05, std_change * 50))  # 0.05 ~ 0.95 범위로 정규화
            
            return volatility
        
        # 기본값 (실제 데이터가 없을 때)
        return {
            '005930': 0.023,  # 삼성전자: 일평균 2.3% 변동
            '000660': 0.028,  # SK하이닉스: 일평균 2.8% 변동
            '005380': 0.018,  # 현대차: 일평균 1.8% 변동
            '005490': 0.021,  # 포스코: 일평균 2.1% 변동
            '051910': 0.025,  # LG화학: 일평균 2.5% 변동
            '097950': 0.016,  # CJ대한통운: 일평균 1.6% 변동
            '006400': 0.024,  # 삼성SDI: 일평균 2.4% 변동
            '373220': 0.026,  # LG에너지솔루션: 일평균 2.6% 변동
            '096770': 0.020,  # SK이노베이션: 일평균 2.0% 변동
            '055550': 0.015,  # 신한지주: 일평균 1.5% 변동
            '086790': 0.016,  # 하나금융지주: 일평균 1.6% 변동
            '105560': 0.015,  # KB금융지주: 일평균 1.5% 변동
            '138930': 0.018,  # BNK금융지주: 일평균 1.8% 변동
            '323410': 0.025,  # 카카오뱅크: 일평균 2.5% 변동
            '028260': 0.019,  # 삼성물산: 일평균 1.9% 변동
            '009540': 0.017,  # 한샘: 일평균 1.7% 변동
            '010140': 0.022,  # 삼성전기: 일평균 2.2% 변동
            '017670': 0.016,  # SK텔레콤: 일평균 1.6% 변동
            '030200': 0.016,  # KT: 일평균 1.6% 변동
            '015760': 0.014,  # 한국전력: 일평균 1.4% 변동
            '068270': 0.029,  # 셀트리온: 일평균 2.9% 변동
            '207940': 0.030   # 삼성바이오로직스: 일평균 3.0% 변동
        }
    
    def calculate_realistic_change(
        self, 
        event: Dict, 
        stock_code: str,
        current_price: float,
        market_sentiment: float = 0.0
    ) -> Dict[str, float]:
        """
        현실적인 주가 변동을 계산 (실제 데이터 기반)
        
        Args:
            event: 이벤트 정보 (type, category, sentiment, impact_level)
            stock_code: 주식 코드
            current_price: 현재 주가
            market_sentiment: 전체 시장 분위기 (-1.0 ~ 1.0)
        
        Returns:
            Dict: {'delta': 변동률, 'price': 새 가격, 'volume': 거래량 변화}
        """
        if stock_code not in self.stock_characteristics:
            return {'delta': 0.0, 'price': current_price, 'volume': 1.0}
        
        stock_spec = self.stock_characteristics[stock_code]
        event_type = event.get('event_type', '')
        event_category = event.get('category', '')
        event_sentiment = event.get('sentiment', 0.0)
        event_impact = event.get('impact_level', 1) / 5.0  # 1-5 → 0.0-1.0
        
        # 1. 섹터 연관성 체크
        sector_correlation = self._get_sector_correlation(event_category, stock_spec['sector'])
        if sector_correlation <= 0.0:
            return {'delta': 0.0, 'price': current_price, 'volume': 1.0}
        
        # 2. 기본 영향도 계산 (섹터 연관성 반영)
        base_impact = event_impact * sector_correlation * stock_spec['news_sensitivity']
        
        # 3. 섹터별 가중치 적용
        sector_weight = stock_spec['sector_weight']
        weighted_impact = base_impact * (0.5 + 0.5 * sector_weight)
        
        # 4. 감정 점수 반영
        sentiment_multiplier = 1.0 + (event_sentiment * 0.5)  # -0.5 ~ 1.5
        sentiment_impact = weighted_impact * sentiment_multiplier
        
        # 5. 변동성 조정 (실제 데이터 기반)
        volatility_factor = stock_spec['volatility']
        volatility_impact = sentiment_impact * volatility_factor
        
        # 6. 시장 규모별 조정
        market_cap_multiplier = self._get_market_cap_multiplier(stock_spec['market_cap'])
        market_cap_impact = volatility_impact * market_cap_multiplier
        
        # 7. 실제 데이터 기반 현실적 범위 제한
        if stock_code in self.volatility_patterns:
            # 실제 데이터의 패턴을 반영
            pattern = self.volatility_patterns[stock_code]
            actual_std = pattern['std_change']
            actual_max = pattern['max_change']
            
            # 실제 데이터 기반 최대 변동폭 계산
            max_daily_change = min(0.15, max(actual_max * 1.5, actual_std * 4))
            
            # 연속성 패턴 반영 (실제 데이터의 상관관계 반영)
            if pattern['correlation'] > 0.1:  # 양의 상관관계가 있으면 변동성 증가
                market_cap_impact *= (1.0 + pattern['correlation'] * 0.3)
            elif pattern['correlation'] < -0.1:  # 음의 상관관계가 있으면 변동성 감소
                market_cap_impact *= (1.0 + pattern['correlation'] * 0.2)
        else:
            # 기본값 사용
            historical_vol = self.historical_volatility.get(stock_code, 0.02)
            max_daily_change = min(0.15, historical_vol * 5)
        
        # 8. 최종 변동률 계산 (현실적 범위 내)
        final_delta = np.clip(market_cap_impact, -max_daily_change, max_daily_change)
        
        # 9. 실제 데이터 기반 노이즈 추가
        if stock_code in self.volatility_patterns:
            # 실제 데이터의 표준편차를 기반으로 한 노이즈
            actual_std = self.volatility_patterns[stock_code]['std_change']
            noise_std = actual_std * 0.3  # 실제 변동성의 30% 수준의 노이즈
            noise = np.random.normal(0, noise_std)
            final_delta += noise
        else:
            # 기본 노이즈
            noise = random.uniform(-0.005, 0.005)
            final_delta += noise
        
        # 10. 거래량 변화 계산 (실제 데이터 패턴 반영)
        volume_change = self._calculate_volume_change(
            abs(final_delta), 
            stock_spec['base_volume'],
            event_impact,
            stock_spec['news_sensitivity'],
            stock_code
        )
        
        # 11. 새 가격 계산
        new_price = current_price * (1.0 + final_delta)
        
        return {
            'delta': round(final_delta, 4),
            'price': round(new_price, 2),
            'volume': volume_change
        }
    
    def _get_sector_correlation(self, event_category: str, stock_sector: str) -> float:
        """이벤트 카테고리와 주식 섹터 간의 연관성 반환"""
        # 이벤트 카테고리와 섹터 매핑
        category_sector_map = {
            '기술': ['IT/전자', '바이오', '화학'],
            '정부': ['금융', '에너지', '건설'],
            '경제': ['금융', 'IT/전자', '자동차'],
            '사회': ['소비재', '통신', '물류/운송'],
            '국제': ['IT/전자', '자동차', '화학'],
            '금융': ['금융', 'IT/전자'],
            '산업': ['화학', '철강/소재', '에너지'],
            '정치': ['금융', '건설', '에너지']
        }
        
        if event_category in category_sector_map:
            if stock_sector in category_sector_map[event_category]:
                return 1.0  # 직접 관련
            else:
                # 간접 관련성 계산
                return self._calculate_indirect_correlation(event_category, stock_sector)
        
        return 0.3  # 기본값: 약한 관련성
    
    def _calculate_indirect_correlation(self, event_category: str, stock_sector: str) -> float:
        """간접적인 섹터 연관성 계산"""
        # 간단한 규칙 기반 계산
        if event_category in ['기술', '경제']:
            if stock_sector in ['IT/전자', '바이오']:
                return 0.6  # 중간 관련성
            elif stock_sector in ['화학', '자동차']:
                return 0.4  # 약한 관련성
            else:
                return 0.2  # 매우 약한 관련성
        
        elif event_category in ['정부', '정치']:
            if stock_sector in ['금융', '에너지']:
                return 0.5  # 중간 관련성
            else:
                return 0.1  # 매우 약한 관련성
        
        return 0.2  # 기본값
    
    def _get_market_cap_multiplier(self, market_cap: str) -> float:
        """시장 규모별 가중치"""
        multipliers = {
            'large': 0.8,    # 대형주: 안정적, 변동 적음
            'medium': 1.0,   # 중형주: 기본
            'small': 1.3     # 소형주: 변동 큼
        }
        return multipliers.get(market_cap, 1.0)
    
    def _calculate_volume_change(
        self, 
        price_change: float, 
        base_volume: int,
        event_impact: float,
        news_sensitivity: float,
        stock_code: str = None
    ) -> float:
        """거래량 변화 계산 (실제 데이터 패턴 반영)"""
        # 가격 변동이 클수록 거래량 증가
        volume_multiplier = 1.0 + (price_change * 3.0)  # 최대 4배
        
        # 이벤트 영향도가 클수록 거래량 증가
        event_volume_multiplier = 1.0 + (event_impact * 2.0)
        
        # 뉴스 민감도가 높을수록 거래량 증가
        sensitivity_multiplier = 1.0 + (news_sensitivity * 0.5)
        
        # 실제 데이터 패턴 반영
        if stock_code and stock_code in self.volatility_patterns:
            pattern = self.volatility_patterns[stock_code]
            
            # 극단적 변동이 자주 발생하는 종목은 거래량 변화도 큼
            if pattern['extreme_ratio'] > 0.1:  # 10% 이상 극단적 변동
                volume_multiplier *= 1.2
            
            # 연속성 패턴 반영
            if pattern['max_consecutive_up'] > 3 or pattern['max_consecutive_down'] > 3:
                volume_multiplier *= 1.1
        
        # 랜덤 요소 추가
        random_factor = random.uniform(0.8, 1.2)
        
        final_multiplier = volume_multiplier * event_volume_multiplier * sensitivity_multiplier * random_factor
        
        return round(final_multiplier, 2)
    
    def get_stock_summary(self, stock_code: str) -> Dict:
        """주식 요약 정보 반환 (실제 데이터 포함)"""
        if stock_code not in self.stock_characteristics:
            return {}
        
        spec = self.stock_characteristics[stock_code]
        summary = {
            'code': stock_code,
            'name': spec['name'],
            'sector': spec['sector'],
            'market_cap': spec['market_cap'],
            'volatility': spec['volatility'],
            'news_sensitivity': spec['news_sensitivity'],
            'historical_volatility': self.historical_volatility.get(stock_code, 0.02)
        }
        
        # 실제 데이터 패턴 정보 추가
        if stock_code in self.volatility_patterns:
            pattern = self.volatility_patterns[stock_code]
            summary.update({
                'actual_std': pattern['std_change'],
                'actual_max': pattern['max_change'],
                'extreme_ratio': pattern['extreme_ratio'],
                'correlation': pattern['correlation'],
                'data_points': pattern['data_points']
            })
        
        return summary
    
    def get_all_stocks_summary(self) -> List[Dict]:
        """모든 주식 요약 정보 반환"""
        return [self.get_stock_summary(code) for code in self.stock_characteristics.keys()]
    
    def get_market_overview(self) -> Dict:
        """전체 시장 개요 반환"""
        if not self.volatility_patterns:
            return {}
        
        # 섹터별 평균 변동성
        sector_volatility = {}
        for ticker, pattern in self.volatility_patterns.items():
            if ticker in self.stock_characteristics:
                sector = self.stock_characteristics[ticker]['sector']
                if sector not in sector_volatility:
                    sector_volatility[sector] = []
                sector_volatility[sector].append(pattern['std_change'])
        
        # 섹터별 평균 계산
        sector_avg = {}
        for sector, vols in sector_volatility.items():
            sector_avg[sector] = {
                'avg_volatility': np.mean(vols),
                'stock_count': len(vols)
            }
        
        return {
            'total_stocks': len(self.volatility_patterns),
            'sector_volatility': sector_avg,
            'overall_avg_volatility': np.mean([p['std_change'] for p in self.volatility_patterns.values()]),
            'data_quality': '실제 데이터 기반' if self.volatility_patterns else '기본값 사용'
        } 