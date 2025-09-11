# SAMS 테스트 시스템

Firebase API 호출 없이 로컬에서 데이터베이스 관련 테스트를 실행할 수 있는 시스템입니다.

## 🎯 주요 기능

- **Firebase API 호출 최소화**: 실제 Firebase 호출 없이 테스트 실행
- **TSV 형식 로그**: 테스트 결과를 탭 구분 형식으로 저장
- **JSON 데이터 저장**: 상세한 테스트 데이터를 JSON으로 저장
- **성능 벤치마크**: 다양한 데이터 크기로 성능 테스트
- **모킹 시스템**: Firebase 기능을 완전히 모킹

## 📁 파일 구조

```
tests/
├── README.md                    # 이 파일
├── run_tests.py                 # 테스트 실행 스크립트
├── integrated_database_test.py  # 통합 테스트
├── test_logger.py              # 테스트 로거 시스템
├── mock_firebase.py            # Firebase 모킹 시스템
├── test_data_generator.py      # 테스트 데이터 생성기
└── logs/                       # 생성된 로그 파일들
    ├── *.tsv                   # TSV 형식 로그
    └── *.json                  # JSON 형식 데이터
```

## 🚀 사용법

### 1. 간단한 실행
```bash
cd tests
python run_tests.py
```

### 2. 개별 테스트 실행
```bash
# 통합 데이터베이스 테스트
python integrated_database_test.py

# 데이터 생성기 테스트
python test_data_generator.py

# Firebase 모킹 테스트
python mock_firebase.py

# 로거 시스템 테스트
python test_logger.py
```

## 📊 생성되는 파일들

### TSV 파일 (탭 구분 형식)
- `integrated_database_test_YYYYMMDD_HHMMSS.tsv`: 테스트 실행 로그
- `export_test_simulations_YYYYMMDD_HHMMSS.tsv`: 시뮬레이션 데이터
- `export_test_events_YYYYMMDD_HHMMSS.tsv`: 이벤트 데이터
- `export_test_news_YYYYMMDD_HHMMSS.tsv`: 뉴스 데이터
- `export_test_snapshots_YYYYMMDD_HHMMSS.tsv`: 스냅샷 데이터

### JSON 파일
- `integrated_database_test_YYYYMMDD_HHMMSS.json`: 상세 테스트 데이터
- `integrated_database_test_summary.json`: 테스트 요약 정보
- `export_test_complete_YYYYMMDD_HHMMSS.json`: 전체 데이터
- `export_test_statistics_YYYYMMDD_HHMMSS.json`: 통계 정보

## 🔧 테스트 구성 요소

### 1. TestLogger
- 테스트 결과를 TSV 형식으로 저장
- 실행 시간, 상태, 오류 메시지 등 기록
- JSON 형식으로 상세 데이터 저장

### 2. MockFirebaseSystem
- Firebase Firestore 기능을 완전히 모킹
- 실제 API 호출 없이 데이터베이스 작업 시뮬레이션
- 통계 조회, 데이터 생성/조회 기능 제공

### 3. TestDataGenerator
- 현실적인 테스트 데이터 생성
- 시뮬레이션, 이벤트, 뉴스, 스냅샷 데이터 생성
- TSV 및 JSON 형식으로 데이터 내보내기

### 4. IntegratedDatabaseTest
- 모든 테스트를 통합하여 실행
- 성능 벤치마크 포함
- 종합적인 테스트 결과 제공

## 📈 성능 벤치마크

시스템은 다양한 데이터 크기로 성능을 테스트합니다:

- **1개 시뮬레이션**: ~1ms (63,974 records/sec)
- **3개 시뮬레이션**: ~1ms (158,912 records/sec)
- **5개 시뮬레이션**: ~2ms (108,714 records/sec)
- **10개 시뮬레이션**: ~4ms (144,535 records/sec)

## 🎯 테스트 항목

### 1. 데이터 생성 테스트
- 시뮬레이션 데이터 생성
- 이벤트, 뉴스, 스냅샷 데이터 생성
- 실행 시간 및 성능 측정

### 2. Firebase 모킹 테스트
- 모킹된 Firebase 시스템 동작 확인
- 통계 조회 기능 테스트
- 데이터 무결성 검증

### 3. 데이터 내보내기 테스트
- TSV 형식으로 데이터 내보내기
- JSON 형식으로 데이터 내보내기
- 파일 생성 및 저장 확인

### 4. 성능 벤치마크 테스트
- 다양한 데이터 크기로 성능 측정
- 처리 속도 및 메모리 사용량 확인
- 확장성 검증

## 🔍 로그 분석

### TSV 파일 분석
```bash
# Windows PowerShell
Get-Content logs/integrated_database_test_*.tsv | Select-Object -First 10

# Linux/Mac
head -10 logs/integrated_database_test_*.tsv
```

### JSON 파일 분석
```python
import json

# 통계 정보 확인
with open('logs/integrated_database_test_summary.json', 'r') as f:
    summary = json.load(f)
    print(f"총 실행 시간: {summary['total_execution_time_seconds']}초")
    print(f"전체 상태: {summary['overall_status']}")
```

## 🛠️ 커스터마이징

### 테스트 데이터 크기 조정
```python
# integrated_database_test.py에서 수정
data = self.data_generator.generate_all_test_data(num_simulations=10)  # 기본값: 3
```

### 로그 디렉토리 변경
```python
# test_logger.py에서 수정
logger = TestLogger("test_name", log_dir="custom_logs")
```

### 성능 벤치마크 범위 조정
```python
# integrated_database_test.py에서 수정
test_sizes = [1, 5, 10, 20]  # 기본값: [1, 3, 5, 10]
```

## 📝 주의사항

1. **Firebase API 호출 없음**: 이 테스트 시스템은 실제 Firebase에 연결하지 않습니다.
2. **로컬 파일 저장**: 모든 데이터는 로컬 파일로 저장됩니다.
3. **메모리 사용량**: 대용량 데이터 생성 시 메모리 사용량이 증가할 수 있습니다.
4. **파일 권한**: logs/ 폴더에 대한 쓰기 권한이 필요합니다.

## 🎉 장점

- **비용 절약**: Firebase API 호출 비용 없이 테스트 가능
- **빠른 실행**: 네트워크 지연 없이 로컬에서 빠르게 실행
- **상세한 로그**: TSV 형식으로 테스트 결과를 쉽게 분석
- **확장 가능**: 새로운 테스트 케이스를 쉽게 추가 가능
- **디버깅 용이**: 상세한 오류 메시지와 실행 로그 제공

