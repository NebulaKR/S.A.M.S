simulation/
├── __init__.py
├── core/                   # 핵심 시뮬레이션 로직
│   ├── event.py            # Event 추상 클래스 및 하위 클래스 정의
│   ├── entities.py         # News, Public, Company, Government 등 내부 요소 정의
│   ├── models.py           # MainModel, Coach, Announcer 모델 정의
│   └── simulation_loop.py  # 시뮬레이션 실행 흐름 정의
│
├── data/                   # 데이터 정의 및 샘플/초기 JSON
│   ├── initial_state.json
│   └── ...
│
├── utils/                  # 공통 도우미 함수 (ex. JSON 직렬화, 로그 등)
│   ├── json_helper.py
│   ├── logger.py
│   └── ...
│
└── main.py                 # 실행 엔트리 포인트