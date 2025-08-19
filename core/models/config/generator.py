import random
from data.parameter_templates import SCENARIO_TEMPLATES
from core.entities import Public, Company, Government, News as NewsEntity

def get_internal_params(seed=None, scenario="default"):
    """
    시뮬레이션에서 사용할 내부 파라미터를 생성하는 함수.
    - 특정 시나리오 템플릿을 기반으로 값을 불러오고
    - 약간의 무작위성(perturbation)을 추가해 실제 사용할 값을 만들어냄.
    
    Parameters:
        seed (int): 결과 재현성을 위한 랜덤 시드 값
        scenario (str): 사용할 시나리오 키워드 (예: "default", "crisis")
    
    Returns:
        dict: 정부, 기업, 대중, 언론 각각에 대한 파라미터 값 딕셔너리
    """
    
    # 랜덤 시드 고정 (재현 가능성 위해)
    if seed is not None:
        random.seed(seed)

    # 지정된 시나리오 템플릿 불러오기 (없으면 default 사용)
    base = SCENARIO_TEMPLATES.get(scenario, SCENARIO_TEMPLATES["default"])

    # 각 값에 소규모 무작위 조정값을 더하는 함수
    def perturb(value, scale=0.1):
        return round(value + random.uniform(-scale, scale), 3)

    result = {}

    # 시나리오 템플릿의 각 섹션(정부, 기업, 대중, 언론)에 대해 반복
    for section, params in base.items():
        result[section] = {}
        for key, val in params.items():
            if isinstance(val, dict):
                # 중첩된 딕셔너리 처리 (예: industry_support)
                result[section][key] = {k: perturb(v, 0.05) for k, v in val.items()}
            else:
                # 단일 값 처리
                result[section][key] = perturb(val)
    
    return result


def build_entities_from_params(params: dict) -> dict:
    """
    dict 형태의 내부 파라미터를 엔티티 인스턴스로 변환해 반환.
    반환 딕셔너리 키: {"public", "company", "government", "news"}
    """
    gov = params.get("government", {})
    comp = params.get("company", {})
    pub = params.get("public", {})
    med = params.get("media", {})

    # 값 매핑/보정
    policy_direction_signed = float(gov.get("policy_direction", 0.0)) * 2.0 - 1.0
    interest_rate = float(gov.get("interest_rate", 0.02))
    tax_policy_signed = float(gov.get("tax_policy", 0.0))  # 이미 -1~+1 사용
    industry_support = dict(gov.get("industry_support", {}))

    government = Government(
        policy_direction=policy_direction_signed,
        interest_rate=interest_rate,
        tax_policy=tax_policy_signed,
        industry_support=industry_support,
    )

    orientation_signed = float(comp.get("trait", 0.0)) * 2.0 - 1.0
    rnd_focus = float(comp.get("rnd_ratio", 0.3))
    volatility = float(comp.get("industry_match", 0.5))  # 정합성을 변동성 근사로 사용
    company = Company(
        industry="Generic",
        orientation=orientation_signed,
        size="중견",
        rnd_focus=rnd_focus,
        volatility=volatility,
    )

    risk_appetite_signed = float(pub.get("risk_appetite", 0.0))
    news_sensitivity = float(pub.get("news_sensitivity", 0.5))
    public = Public(
        consumer_index=50.0,
        risk_appetite=risk_appetite_signed,
        news_sensitivity=news_sensitivity,
    )

    bias = float(med.get("bias", 0.0))
    credibility = float(med.get("trust", 0.7))
    news = NewsEntity(
        bias=bias,
        credibility=credibility,
        impact_level=3,
        category="General",
        sentiment=0.0,
    )

    return {"public": public, "company": company, "government": government, "news": news}