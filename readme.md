# SAMS (Stock AI Market Simulation)

AI 기반 주식 시장 시뮬레이션 시스템입니다. LLM을 활용하여 현실적인 경제 이벤트를 생성하고, 이를 바탕으로 뉴스 기사를 자동 생성하는 기능을 제공합니다.

## 🚀 주요 기능

### 1. AI 이벤트 생성
- LLM을 활용한 현실적인 경제 이벤트 생성
- 시장 상황과 파라미터를 고려한 적응적 이벤트 생성
- 다양한 카테고리 (경제, 정책, 기업, 기술, 국제) 지원

### 2. 자동 뉴스 기사 생성
- 이벤트 발생 시 자동으로 뉴스 기사 생성
- 15개 언론사의 성향과 신뢰도 반영
- 언론사별 편향성과 신뢰도 차별화

### 3. 실시간 시뮬레이션
- 실시간 주가 변동 시뮬레이션
- 이벤트 기반 시장 영향도 계산
- 파이어베이스 기반 데이터 저장 및 조회

### 4. 웹 대시보드
- 시뮬레이션 상태 모니터링
- 실시간 이벤트 피드
- 뉴스 기사 피드 및 필터링
- 시장 통계 및 분석

### 5. 관리자 대시보드
- 시뮬레이션 중앙 제어 시스템
- 실시간 시뮬레이션 상태 모니터링
- 성능 지표 및 로그 관리
- 시뮬레이션 설정 관리

## 📊 API 엔드포인트

### 시뮬레이션 데이터 API

#### 1. 시뮬레이션 상태 조회
```
GET /api/simulation/status/?simulation_id={sim_id}
```
- 현재 시뮬레이션 상태 및 최신 이벤트 정보 조회
- 응답: 시뮬레이션 ID, 상태, 최신 이벤트, 총 이벤트 수, 마지막 업데이트 시간

#### 2. 최근 이벤트 목록 조회
```
GET /api/simulation/events/?simulation_id={sim_id}&limit={limit}
```
- 최근 발생한 이벤트 목록 조회
- 파라미터: `simulation_id` (시뮬레이션 ID), `limit` (조회 개수, 기본값: 10)
- 응답: 이벤트 목록 (ID, 제목, 카테고리, 감성, 영향도, 영향받는 종목, 시장 영향도 등)

#### 3. 이벤트 상세 정보 조회
```
GET /api/simulation/events/detail/?simulation_id={sim_id}&event_id={event_id}
```
- 특정 이벤트의 상세 정보 및 관련 뉴스 기사 조회
- 파라미터: `simulation_id`, `event_id`
- 응답: 이벤트 상세 정보, 관련 뉴스 기사 목록

#### 4. 뉴스 피드 조회
```
GET /api/simulation/news/?simulation_id={sim_id}&limit={limit}&media={media_name}
```
- 생성된 뉴스 기사 피드 조회
- 파라미터: `simulation_id`, `limit` (기본값: 20), `media` (언론사 필터, 선택사항)
- 응답: 뉴스 기사 목록 (언론사, 기사 내용, 성향, 신뢰도, 관련 이벤트 정보)

#### 5. 시장 요약 정보 조회
```
GET /api/simulation/market-summary/?simulation_id={sim_id}
```
- 시장 통계 및 요약 정보 조회
- 응답: 총 이벤트 수, 카테고리별 분포, 평균 감성, 평균 영향도, 시장 분위기, 변동성 등

### 관리자 시뮬레이션 제어 API

#### 1. 시뮬레이션 시작
```
POST /api/admin/simulation/start/
```
- 시뮬레이션 프로세스 시작
- 파라미터: `simulation_id`, `settings` (이벤트 생성 간격, 뉴스 생성 여부, 최대 이벤트 수 등)
- 관리자 권한 필요

#### 2. 시뮬레이션 정지
```
POST /api/admin/simulation/stop/
```
- 시뮬레이션 프로세스 정지
- 파라미터: `simulation_id`
- 관리자 권한 필요

#### 3. 시뮬레이션 상태 조회
```
GET /api/admin/simulation/status/?simulation_id={sim_id}
```
- 시뮬레이션 프로세스 상태 및 성능 지표 조회
- 응답: 상태, 경과 시간, 총 이벤트/뉴스 수, CPU/메모리 사용률, 이벤트/분 등

#### 4. 시뮬레이션 로그 조회
```
GET /api/admin/simulation/logs/?simulation_id={sim_id}&limit={limit}
```
- 시뮬레이션 실행 로그 조회
- 파라미터: `simulation_id`, `limit` (로그 개수, 기본값: 50)

#### 5. 시뮬레이션 설정 업데이트
```
POST /api/admin/simulation/settings/
```
- 시뮬레이션 설정 업데이트
- 파라미터: 이벤트 생성 간격, 시뮬레이션 속도, 허용 카테고리, 뉴스 생성 여부 등

### 포트폴리오 API (기존)

#### 주식 매수/매도
```
POST /api/portfolio/buy/
POST /api/portfolio/sell/
```
- 파라미터: `ticker` (종목 코드), `quantity` (수량), `price` (가격)

#### 관심종목 관리
```
POST /api/portfolio/watchlist/add/
POST /api/portfolio/watchlist/remove/
```
- 파라미터: `ticker` (종목 코드)

#### 포트폴리오 데이터 조회
```
GET /api/portfolio/data/
```
- 현재 포트폴리오 상태 및 수익률 정보

## 🏗️ 시스템 구조

### 핵심 컴포넌트

#### 1. SimulationEngine (`core/models/simulation_engine.py`)
- 시뮬레이션의 핵심 엔진
- 이벤트 생성, 주가 업데이트, 뉴스 생성 트리거
- 시장 상태 모니터링 및 스냅샷 저장

#### 2. SimulationService (`sams/services.py`)
- 시뮬레이션 프로세스 관리 서비스
- 다중 시뮬레이션 동시 실행 지원
- 시뮬레이션 상태 모니터링 및 제어

#### 3. Announcer (`core/models/announcer/announcer.py`)
- LLM 기반 이벤트 및 뉴스 생성
- 파이어베이스 데이터 기반 뉴스 생성
- 언론사별 편향성 반영

#### 4. Firebase Integration (`utils/logger.py`)
- 이벤트 로그, 뉴스 기사, 시장 스냅샷 저장/조회
- 실시간 데이터 동기화

#### 5. Web Dashboard
- Django 기반 웹 인터페이스
- 시뮬레이션 대시보드 (`simulation_dashboard.html`)
- 뉴스 대시보드 (`news_dashboard.html`)
- 관리자 대시보드 (`admin_dashboard.html`)
- 실시간 데이터 시각화 및 제어

### 데이터 흐름

```
1. 시뮬레이션 실행
   ↓
2. 이벤트 생성 (LLM)
   ↓
3. 이벤트 로그 저장 (Firebase)
   ↓
4. 시장 스냅샷 저장 (Firebase)
   ↓
5. 뉴스 기사 생성 (LLM)
   ↓
6. 뉴스 기사 저장 (Firebase)
   ↓
7. 웹 대시보드 업데이트
```

## 🎯 사용법

### 1. 시뮬레이션 실행
```python
from core.models.simulation_engine import SimulationEngine
from data.parameter_templates import get_initial_data

# 초기 데이터 설정
initial_data = get_initial_data()

# 시뮬레이션 엔진 생성
engine = SimulationEngine(initial_data)
engine.enable_news_generation(True)

# 콜백 설정
def on_event_occur(event):
    print(f"새로운 이벤트: {event.event.event_type}")

def on_news_update(news):
    print(f"뉴스 생성: {news.media} - {news.article_text[:50]}...")

engine.add_callback("event_occur", on_event_occur)
engine.add_callback("news_update", on_news_update)

# 시뮬레이션 시작
engine.start()

# 시뮬레이션 루프
while True:
    engine.update()
    time.sleep(1)
```

### 2. 기존 이벤트에 대한 뉴스 생성
```python
from core.models.announcer.announcer import Announcer
from core.models.announcer.news import Media

# Announcer 생성
announcer = Announcer()

# 언론사 설정
media_outlets = [
    Media("조선일보", -0.8, 0.7),
    Media("한겨레", 0.8, 0.8),
    Media("매일경제", 0.0, 0.9),
    # ... 더 많은 언론사
]

# 특정 이벤트에 대한 뉴스 생성
news_list = announcer.generate_news_for_event_from_firestore(
    sim_id="my-simulation",
    event_id="event-123",
    outlets=media_outlets
)
```

### 3. 웹 대시보드 접근
- 시뮬레이션 대시보드: `/simulation/`
- 뉴스 대시보드: `/news/`
- 관리자 대시보드: `/admin/` (관리자 권한 필요)
- 포트폴리오 대시보드: `/portfolio/`

## 📁 데이터 구조

### Firebase 저장 구조

```
simulations/
├── {simulation_id}/
│   ├── events/
│   │   ├── {event_id}/
│   │   │   ├── event_log.json
│   │   │   └── news/
│   │   │       ├── {news_id}.json
│   │   │       └── ...
│   │   └── ...
│   └── snapshots/
│       ├── {snapshot_id}.json
│       └── ...
```

### 이벤트 로그 구조
```json
{
  "event": {
    "id": "event-123",
    "event_type": "AI 칩 수요 폭증",
    "category": "기술",
    "sentiment": 0.8,
    "impact_level": 4,
    "duration": "mid"
  },
  "affected_stocks": ["005930", "000660"],
  "market_impact": 0.15,
  "simulation_time": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00Z",
  "market_context": {
    "market_state": {...},
    "market_params": {...}
  }
}
```

### 뉴스 기사 구조
```json
{
  "news_id": "news-456",
  "media_name": "조선일보",
  "article_text": "AI 서버 수요 증가로 반도체 업계 전망 밝아짐...",
  "created_at": "2024-01-15T10:30:05Z",
  "meta": {
    "outlet_bias": -0.8,
    "outlet_credibility": 0.7,
    "generation_method": "firestore_based"
  }
}
```

## 🎨 언론사 설정

### 언론사별 성향 및 신뢰도

| 언론사 | 성향 (Bias) | 신뢰도 | 설명 |
|--------|-------------|--------|------|
| 조선일보 | -0.8 | 0.7 | 보수적 성향, 중간 신뢰도 |
| 한겨레 | 0.8 | 0.8 | 진보적 성향, 높은 신뢰도 |
| 매일경제 | 0.0 | 0.9 | 중립적 성향, 매우 높은 신뢰도 |
| KBS | 0.2 | 0.8 | 약간 진보적, 높은 신뢰도 |
| MBC | 0.3 | 0.7 | 진보적 성향, 중간 신뢰도 |
| SBS | 0.1 | 0.8 | 중립적, 높은 신뢰도 |
| YTN | 0.0 | 0.9 | 중립적, 매우 높은 신뢰도 |
| 연합뉴스 | 0.0 | 0.9 | 중립적, 매우 높은 신뢰도 |
| 뉴시스 | 0.0 | 0.8 | 중립적, 높은 신뢰도 |
| 이데일리 | 0.1 | 0.8 | 약간 진보적, 높은 신뢰도 |
| 서울경제 | 0.0 | 0.8 | 중립적, 높은 신뢰도 |
| 한국경제 | 0.0 | 0.9 | 중립적, 매우 높은 신뢰도 |
| 아시아경제 | 0.0 | 0.8 | 중립적, 높은 신뢰도 |
| 헤럴드경제 | 0.0 | 0.8 | 중립적, 높은 신뢰도 |

### 성향 (Bias) 범위
- **-1.0 ~ -0.3**: 보수적 성향
- **-0.3 ~ 0.3**: 중립적 성향  
- **0.3 ~ 1.0**: 진보적 성향

### 신뢰도 (Credibility) 범위
- **0.0 ~ 0.3**: 낮은 신뢰도
- **0.3 ~ 0.7**: 중간 신뢰도
- **0.7 ~ 1.0**: 높은 신뢰도

## 🔧 설정 및 환경

### 필수 환경 변수
```bash
# Firebase 설정
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# LLM 설정 (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b

# Django 설정
SECRET_KEY=your-secret-key
DEBUG=True
```

### 의존성 설치
```bash
pip install -r requirements.txt
```

### 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

## 🚀 성능 최적화

### 1. 뉴스 생성 최적화
- 배치 처리로 여러 이벤트 동시 처리
- 캐싱을 통한 중복 요청 방지
- 비동기 처리로 응답 시간 단축

### 2. 데이터베이스 최적화
- 인덱싱을 통한 조회 성능 향상
- 페이지네이션으로 대용량 데이터 처리
- 압축을 통한 저장 공간 절약

### 3. 웹 대시보드 최적화
- 실시간 업데이트로 사용자 경험 향상
- 필터링 및 검색 기능으로 데이터 접근성 개선
- 반응형 디자인으로 다양한 디바이스 지원

## 🐛 문제 해결

### 일반적인 문제들

#### 1. Firebase 연결 오류
- 서비스 계정 키 파일 경로 확인
- Firebase 프로젝트 설정 확인
- 네트워크 연결 상태 확인

#### 2. LLM 응답 오류
- Ollama 서버 실행 상태 확인
- 모델 로딩 상태 확인
- 프롬프트 형식 검증

#### 3. 뉴스 생성 실패
- 이벤트 로그 존재 여부 확인
- 언론사 설정 검증
- LLM 응답 파싱 오류 확인

### 디버깅 도구

#### 1. 로그 확인
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 뉴스 내용 확인
```bash
python check_news_content.py
```

#### 3. 시뮬레이션 테스트
```bash
python test_news_generation.py
```

## 📈 향후 개발 계획

### 단기 계획
- [ ] 실시간 웹소켓 지원
- [ ] 더 많은 언론사 추가
- [ ] 뉴스 기사 품질 개선
- [ ] 모바일 앱 개발

### 장기 계획
- [ ] 다국어 지원
- [ ] 고급 분석 기능
- [ ] 머신러닝 모델 통합
- [ ] 클라우드 배포 지원

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.