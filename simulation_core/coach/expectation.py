def calculate_expectation(weights, params):
    """
    내부 파라미터와 가중치를 기반으로 시뮬레이션의 '기대값'을 계산하는 함수.
    이 기대값은 주가 상승/하락의 추정치로 활용될 수 있음.

    Parameters:
        weights (dict): 코치(Coach)가 계산한 각 요소별 가중치 (뉴스, 대중, 기업, 정부)
        params (dict): 시뮬레이션에서 설정된 내부 파라미터 (public, company, government 등)

    Returns:
        float: 기대값 (주가 영향 예측값)
    """

    # 내부 파라미터 분리
    p = params["public"]     # 대중의 심리/성향 관련 파라미터
    c = params["company"]    # 기업 특성 관련 파라미터
    g = params["government"] # 정부 정책 관련 파라미터
    w = weights              # 코치가 조정한 가중치 세트

    # 기대값 계산 로직
    result = (
        w["w_news"] * 0.1 +                     # 뉴스는 고정값 0.1로 가정 (나중에 NewsImpact로 대체 가능)
        w["w_public"] * p["risk_appetite"] +    # 대중이 리스크를 감수할수록 기대 수익이 커짐
        w["w_company"] * c["trait"] +           # 기업 성향이 공격적일수록 기대 상승 여지 존재
        w["w_gov"] * g["policy_direction"]      # 정부 정책이 시장 우호적이면 상승 가능성 반영
    )
    #이후에 여러 파라미터 도입하여 확장(p, c, g)

    return round(result, 4)
    # 소수점 4자리까지 반올림하여 반환