# SAMS 뉴스 기사 생성 기능

## 개요

SAMS(Stock AI Market Simulation) 시스템에서 이벤트 발생 후 자동으로 뉴스 기사를 생성하는 기능입니다. 파이어스토어에 저장된 이벤트 로그를 기반으로 다양한 언론사의 성향과 신뢰도를 반영한 뉴스 기사를 생성합니다.

## 주요 기능

### 1. 자동 뉴스 기사 생성
- 이벤트 발생 시 자동으로 뉴스 기사 생성
- 15개 주요 언론사 설정 (보수/진보/중립 성향)
- 언론사별 성향과 신뢰도 반영
- 파이어스토어에 이벤트 로그와 뉴스 기사 저장

### 2. 언론사 설정
- **보수적 언론**: 조선일보, 중앙일보, 한국일보, 동아일보
- **진보적 언론**: 경향신문, 한겨레
- **중립 언론**: 서울신문, 매일경제, 한국경제, 이데일리, 머니투데이
- **방송사**: SBS, KBS, MBC, YTN

### 3. 뉴스 생성 프로세스
1. 이벤트 발생 → 파이어스토어에 이벤트 로그 저장
2. 이벤트 로그 조회 → 컨텍스트용 최근 이벤트들 조회
3. 각 언론사별 뉴스 기사 생성 → LLM을 통한 자연어 생성
4. 생성된 뉴스 기사를 파이어스토어에 저장

## 사용법

### 1. 시뮬레이션에서 뉴스 기사 생성 활성화

```python
from core.models.simulation_engine import SimulationEngine

# 시뮬레이션 엔진 초기화
engine = SimulationEngine(initial_data)

# 뉴스 기사 생성 활성화
engine.enable_news_generation(True)

# 뉴스 업데이트 콜백 등록
def on_news_update(news):
    print(f"뉴스 생성: {news.media} - {news.id}")

engine.add_callback("news_update", on_news_update)

# 시뮬레이션 시작
engine.start()
```

### 2. 기존 이벤트에 대한 뉴스 기사 생성

```python
from core.models.announcer.announcer import Announcer
from core.models.announcer.news import Media

# Announcer 초기화
announcer = Announcer()

# 언론사 설정
outlets = [
    Media(name="조선일보", bias=-0.8, credibility=0.7),      # 보수적
    Media(name="한겨레", bias=0.7, credibility=0.8),         # 진보적
    Media(name="매일경제", bias=0.0, credibility=0.8),       # 중립 (경제 전문)
]

# 특정 이벤트에 대한 뉴스 기사 생성
news_list = announcer.generate_news_for_event_from_firestore(
    sim_id="your_simulation_id",
    event_id="event_123",
    outlets=outlets,
    context_events_limit=5
)

print(f"{len(news_list)}개의 뉴스 기사가 생성되었습니다.")
```

### 3. 여러 이벤트에 대한 일괄 뉴스 기사 생성

```python
# 여러 이벤트 ID 목록
event_ids = ["event_1", "event_2", "event_3"]

# 일괄 뉴스 기사 생성
results = announcer.generate_news_for_multiple_events(
    sim_id="your_simulation_id",
    event_ids=event_ids,
    outlets=outlets,
    context_events_limit=5
)

# 결과 확인
for event_id, news_list in results.items():
    print(f"이벤트 {event_id}: {len(news_list)}개 뉴스 기사")
```

### 4. 테스트 스크립트 실행

```bash
# 뉴스 기사 생성 기능 테스트
python test_news_generation.py
```

## 저장되는 데이터 구조

### 이벤트 로그
```json
{
  "event": {
    "id": "event_123",
    "event_type": "기업 실적 발표",
    "category": "기업",
    "sentiment": 0.3,
    "impact_level": 4,
    "duration": "mid"
  },
  "affected_stocks": ["005930", "000660"],
  "market_impact": 0.15,
  "simulation_time": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00",
  "meta": {"reason": "event_occurred"}
}
```

### 뉴스 기사
```json
{
  "news_id": "news_456",
  "media_name": "조선일보",
  "article_text": "삼성전자가 예상치를 상회하는 실적을 발표했다...",
  "created_at": "2024-01-15T10:30:30",
  "meta": {
    "outlet_bias": -0.8,
    "outlet_credibility": 0.7,
    "generation_method": "firestore_based"
  }
}
```

## Firebase 저장 구조

```
simulations/
  {simulation_id}/
    events/
      {event_id}/
        - event: {...}
        - affected_stocks: [...]
        - market_impact: 0.15
        - simulation_time: "..."
        - created_at: "..."
        - meta: {...}
        news/
          {news_id}/
            - news_id: "..."
            - media_name: "조선일보"
            - article_text: "..."
            - created_at: "..."
            - meta: {...}
    snapshots/
      {snapshot_id}/
        - stocks: {...}
        - market_params: {...}
        - simulation_time: "..."
        - created_at: "..."
        - meta: {...}
```

## 언론사 성향 설정

### Bias (편향성)
- **-1.0 ~ -0.5**: 보수적 언론
- **-0.5 ~ 0.5**: 중립 언론
- **0.5 ~ 1.0**: 진보적 언론

### Credibility (신뢰도)
- **0.0 ~ 1.0**: 언론사의 신뢰도 (높을수록 신뢰도 높음)

### 언론사별 설정
```python
Media(name="조선일보", bias=-0.8, credibility=0.7),      # 보수적
Media(name="중앙일보", bias=-0.6, credibility=0.8),      # 보수적
Media(name="한국일보", bias=-0.7, credibility=0.6),      # 보수적
Media(name="동아일보", bias=-0.5, credibility=0.7),      # 중도보수
Media(name="경향신문", bias=0.6, credibility=0.7),       # 진보적
Media(name="한겨레", bias=0.7, credibility=0.8),         # 진보적
Media(name="서울신문", bias=0.0, credibility=0.6),       # 중립
Media(name="매일경제", bias=0.0, credibility=0.8),       # 중립 (경제 전문)
Media(name="한국경제", bias=0.0, credibility=0.7),       # 중립 (경제 전문)
Media(name="이데일리", bias=0.0, credibility=0.6),       # 중립
Media(name="머니투데이", bias=0.0, credibility=0.7),     # 중립 (경제 전문)
Media(name="SBS", bias=0.0, credibility=0.8),            # 중립 (방송)
Media(name="KBS", bias=0.0, credibility=0.9),            # 중립 (방송)
Media(name="MBC", bias=0.1, credibility=0.8),            # 약간 진보 (방송)
Media(name="YTN", bias=0.0, credibility=0.7),            # 중립 (방송)
```

## 뉴스 생성 프롬프트 구조

### 입력 정보
1. **과거 이벤트 컨텍스트**: 최근 5개 이벤트 요약
2. **현재 이벤트 정보**: 
   - 이벤트 제목, 카테고리, 감성 점수
   - 영향 수준, 지속 기간
   - 영향받는 종목, 시장 영향도
3. **언론사 정보**: 이름, 성향, 신뢰도

### 출력 요구사항
- 뉴스 기사 본문만 출력
- 250~400자 내외
- 한국어로 자연스럽게 작성
- 언론사 성향에 따른 보도 톤 조절

## 성능 최적화

### 1. 뉴스 생성 빈도 조정
```python
# 뉴스 생성 비활성화 (성능 향상)
engine.enable_news_generation(False)

# 필요한 시점에만 수동으로 뉴스 생성
announcer.generate_news_for_event_from_firestore(...)
```

### 2. 컨텍스트 이벤트 수 조정
```python
# 컨텍스트로 사용할 이벤트 수 조정
news_list = announcer.generate_news_for_event_from_firestore(
    sim_id=sim_id,
    event_id=event_id,
    outlets=outlets,
    context_events_limit=3  # 기본값: 5
)
```

### 3. 언론사 수 조정
```python
# 테스트용으로 일부 언론사만 선택
test_outlets = [
    Media(name="조선일보", bias=-0.8, credibility=0.7),
    Media(name="한겨레", bias=0.7, credibility=0.8),
    Media(name="매일경제", bias=0.0, credibility=0.8),
]
```

## 확장 가능한 기능

### 1. 뉴스 기사 분석
- 감정 분석 (긍정/부정/중립)
- 키워드 추출
- 영향도 측정

### 2. 뉴스 기사 필터링
- 특정 언론사만 선택
- 신뢰도 기준 필터링
- 성향별 그룹핑

### 3. 뉴스 기사 통계
- 언론사별 기사 수
- 이벤트별 보도 빈도
- 성향별 보도 패턴

### 4. 실시간 뉴스 피드
- 웹 대시보드에서 실시간 뉴스 표시
- 언론사별 탭 분리
- 검색 및 필터링 기능

## 문제 해결

### 뉴스 기사가 생성되지 않는 경우
1. 이벤트 로그가 파이어스토어에 저장되었는지 확인
2. 시뮬레이션 ID와 이벤트 ID가 올바른지 확인
3. 뉴스 생성이 활성화되어 있는지 확인
4. LLM 서비스 연결 상태 확인

### 뉴스 기사 품질 문제
1. 프롬프트 템플릿 조정
2. 컨텍스트 이벤트 수 증가
3. 언론사 설정 조정
4. LLM 모델 변경

### 성능 이슈
1. 뉴스 생성 빈도 줄이기
2. 언론사 수 줄이기
3. 컨텍스트 이벤트 수 줄이기
4. 비동기 처리 구현

## API 엔드포인트 (향후 구현 예정)

```javascript
// 특정 이벤트의 뉴스 기사 조회
GET /api/events/{event_id}/news

// 언론사별 뉴스 기사 조회
GET /api/news?media=조선일보

// 뉴스 기사 통계
GET /api/news/stats?simulation_id={sim_id}
```
