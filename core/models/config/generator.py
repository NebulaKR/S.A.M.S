import random
from data.parameter_templates import SCENARIO_TEMPLATES

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