## Coach 기능 명세

### 역할
- 내부 파라미터(`public, company, government, media`)와 선택 입력(`events_summary`, `external`)을 사용해 요소별 가중치(`w_news, w_public, w_company, w_gov`) 산출.
- 모든 가중치는 [0,1] 범위로 클리핑 후 합=1 정규화.
- 이벤트/기사 생성 품질 개선을 위한 **피드백 프롬프트 작성 및 편집** 역할을 수행(프롬프트 실험, 톤/편향 보정, 실패 사례 리라이팅 가이드).

### 입력
- `internal_params: dict`
  - `public`: `{ news_sensitivity: float, risk_appetite: float }`
  - `company`: `{ rnd_ratio: float }`
  - `government`: `{ policy_direction: float }`
- `events_summary: Optional[dict]` (확장)
  - 예: `{ surprise_ratio: float, pos_neg_ratio: float }`
- `external: Optional[dict]` (확장)
  - 예: `{ vix: float, fx_rate: float }`

### 출력
```json
{ "w_news": float, "w_public": float, "w_company": float, "w_gov": float }
```

### 기본 공식 (MVP)
- 원천값을 [0,1] 클리핑 후 아래 식 적용
```
w_news    = 0.4 + 0.2 * public.news_sensitivity
w_public  = 0.3 + 0.1 * public.risk_appetite
w_company = 0.2 + 0.2 * company.rnd_ratio
w_gov     = 0.1 + 0.2 * government.policy_direction
```
- 보정(옵션)
  - `events_summary.surprise_ratio` → `w_news += 0.05 * surprise_ratio`
  - `events_summary.pos_neg_ratio` → `w_public += 0.05 * (pos_neg_ratio - 0.5)`
  - `external.vix` → `w_news += 0.05 * vix`
- 이후 `[0,1]` 클리핑 → 합=1 정규화 → 소수 3자리 반올림

### 확장 포인트
- 다중 파라미터: `trait`, `industry_match`, `interest_rate`, `tax_policy` 등 가중식에 반영
- 이벤트 요약: `surprise_ratio`, `pos_neg_ratio`, `direct_impact`에 따른 동적 가중치 조정
- 외부 변수: `vix`, `fx_rate`, `commodity` 등 매크로 환경 변수 반영

### 사용 예시
```python
from core.models.coach.coach import Coach

params = {
  "public": {"news_sensitivity": 0.6, "risk_appetite": 0.2},
  "company": {"rnd_ratio": 0.3},
  "government": {"policy_direction": 0.4}
}
coach = Coach(params)
weights = coach.adjust_weights(events_summary={"surprise_ratio": 0.8})
# {'w_news': ..., 'w_public': ..., 'w_company': ..., 'w_gov': ...}, 합=1
``` 

### 피드백 프롬프트 운영 가이드
- 목적: Event/Article 생성 결과를 검토해 다음 생성 품질을 높이기 위한 피드백 프롬프트를 표준화.
- 입력 예시
  - 최근 생성 산출물: 사건 1건 + 매체별 기사 N건
  - 품질 지표: 사실성, 편향 반영도, 중복도, 문체 안정성
- 출력 예시
  - 유지할 요소(Keep)
  - 개선할 요소(Improve)
  - 다음 호출에 적용할 수정 지시(Edit Prompt)

```text
[피드백 프롬프트 템플릿]
현재 생성된 Event/Article 묶음을 평가하라.
1) 사건 사실과 기사 해석이 혼동된 문장을 식별
2) 매체 bias/credibility 반영이 약한 문장을 수정 방향으로 제시
3) 다음 생성에서 반드시 반영할 3개의 프롬프트 편집안을 출력
출력 형식: Keep 3개 / Improve 3개 / Edit Prompt 3개
```
