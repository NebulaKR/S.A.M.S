# 시뮬레이션 초기 상태에서 각 요소의 파라미터 기본값을 담고 있음
# 각 값은 0~1 또는 -1~1 범위에서 설정되며, 시나리오에 따라 변화 가능

SCENARIO_TEMPLATES = {
    "default": {
        "government": {
            "policy_direction": 0.5,  # 정책 방향성: +면 성장 유도, -면 규제 중심
            "interest_rate": 0.03,    # 금리 수준: 기준금리 (%), 경제활성화/위축 반영
            "tax_policy": -0.2,       # 세금 정책: +면 세금 증가(긴축), -면 감세(부양)
            "industry_support": {     # 산업별 지원 수준 (0~1)
                "AI": 0.6,            # AI 산업에 대한 정책적 우호도
                "Green": 0.3          # 친환경 산업에 대한 정책적 우호도
            }
        },
        "company": {
            "trait": 0.4,             # 기업 성향: +면 공격적, -면 보수적
            "rnd_ratio": 0.3,         # R&D 투자 비율 (연구개발 비중, 0~1)
            "industry_match": 0.8     # 현재 산업 트렌드와의 정합성 (0~1)
        },
        "public": {
            "risk_appetite": -0.1,    # 대중의 리스크 선호도: +면 공격적 투자 성향
            "news_sensitivity": 0.5   # 뉴스에 대한 민감도: 높을수록 심리적 반응 큼
        },
        "media": {
            "bias": 0.2,              # 언론 성향: +면 낙관적, -면 비관적
            "trust": 0.7              # 언론 신뢰도: 대중이 얼마나 신뢰하는지 (0~1)
        }
    }
}


def get_initial_data():
    """
    시뮬레이션 엔진 초기화를 위한 기본 데이터 반환
    
    Returns:
        Dict: 시뮬레이션 엔진이 요구하는 초기 데이터 구조
    """
    return {
        "stocks": {
            "005930": {"price": 79000, "volume": 1000000},  # 삼성전자
            "000660": {"price": 45000, "volume": 500000},   # SK하이닉스
            "035420": {"price": 120000, "volume": 300000},  # NAVER
            "051910": {"price": 180000, "volume": 200000},  # LG화학
            "006400": {"price": 35000, "volume": 400000},   # 삼성SDI
            "035720": {"price": 95000, "volume": 250000},   # 카카오
            "207940": {"price": 280000, "volume": 150000},  # 삼성바이오로직스
            "068270": {"price": 55000, "volume": 350000},   # 셀트리온
            "323410": {"price": 85000, "volume": 180000},   # 카카오뱅크
            "373220": {"price": 42000, "volume": 220000},   # LG에너지솔루션
        },
        "market_params": {
            "public": {
                "risk_appetite": 0.3,
                "news_sensitivity": 0.7
            },
            "government": {
                "policy_direction": 0.2,
                "interest_rate": 0.03,
                "tax_policy": -0.1
            },
            "company": {
                "orientation": 0.1,
                "rnd_focus": 0.4,
                "industry_match": 0.6
            },
            "media": {
                "bias": 0.2,
                "trust": 0.7
            }
        }
    }