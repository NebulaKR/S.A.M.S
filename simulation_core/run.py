# 내부 파라미터 생성 함수 불러오기 (정부, 기업, 대중, 언론 초기값)
from config.generator import get_internal_params

# 코치(Coach) 클래스 - 내부 파라미터 기반으로 가중치 조정
from coach.coach import Coach

# 기대값 계산 함수 - 가중치 + 파라미터 기반으로 기대 주가 변화 계산
from coach.expectation import calculate_expectation

# 딕셔너리를 예쁘게 출력하기 위한 유틸
from pprint import pprint

# 1. 내부 파라미터 생성 (시드 고정으로 결과 재현 가능)
params = get_internal_params(seed=7)

# 생성된 파라미터 전체 출력 (정부, 기업, 대중, 언론 정보 포함)
pprint(params)

# 2. 코치(Coach)를 생성하고 내부 파라미터를 기반으로 가중치 조정
coach = Coach(params)
weights = coach.adjust_weights()

# 계산된 가중치 출력 (뉴스, 대중, 기업, 정부 각각의 영향력)
print("🎯 조정된 가중치:", weights)

# 3. 기대값 계산 (각 요소의 영향력을 바탕으로 기대 주가 변화 추정)
expect = calculate_expectation(weights, params)

# 결과 출력
print("📈 기대값(가중치 적용):", expect)