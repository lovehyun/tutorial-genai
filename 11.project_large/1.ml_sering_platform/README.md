# ML 모델 서빙 플랫폼

ML 모델을 쉽게 배포하고 API로 서빙할 수 있는 플랫폼입니다.

## 주요 기능

- 사용자 인증 및 권한 관리
- ML 모델 업로드 및 관리
- API 키 기반 모델 접근
- 비동기 추론 처리
- 모델 버전 관리
- 다양한 ML 프레임워크 지원 (Scikit-learn, PyTorch, Transformers)
- GPU 리소스 모니터링 및 관리
- 실시간 추론 상태 모니터링

## 기술 스택

- Backend: FastAPI, SQLAlchemy, Celery
- Database: SQLite (개발용), PostgreSQL (프로덕션)
- Cache: Redis
- Frontend: HTML, CSS, JavaScript
- Container: Docker, Docker Compose
- ML Frameworks: Scikit-learn, PyTorch, Transformers

## 프로젝트 구조

```
.
├── app/                    # FastAPI 백엔드
│   ├── api/               # API 엔드포인트
│   │   ├── auth.py       # 인증 관련 API (회원가입, 로그인, 사용자 정보)
│   │   ├── models.py     # 모델 관리 API (업로드, 조회, 삭제)
│   │   ├── api_keys.py   # API 키 관리 API (생성, 조회, 삭제)
│   │   ├── endpoints.py  # 엔드포인트 관리 API (생성, 조회, 수정, 삭제)
│   │   └── inference.py  # 추론 API (추론 요청, 결과 조회)
│   │
│   ├── core/             # 핵심 설정
│   │   ├── config.py     # 환경 설정 관리
│   │   ├── security.py   # 보안 관련 (JWT, 해싱)
│   │   ├── dependencies.py # FastAPI 의존성
│   │   └── redis_client.py # Redis 클라이언트
│   │
│   ├── db/               # 데이터베이스
│   │   ├── models/       # SQLAlchemy 모델
│   │   │   ├── user.py   # 사용자 모델
│   │   │   ├── model.py  # ML 모델 정보
│   │   │   ├── api_key.py # API 키 모델
│   │   │   └── endpoint.py # 엔드포인트 모델
│   │   │
│   │   ├── crud/        # CRUD 작업
│   │   │   ├── user_crud.py
│   │   │   ├── model_crud.py
│   │   │   ├── api_key_crud.py
│   │   │   └── endpoint_crud.py
│   │   │
│   │   ├── database.py  # 데이터베이스 설정
│   │   └── session.py   # DB 세션 관리
│   │
│   ├── schemas/         # Pydantic 모델
│   │   ├── user.py     # 사용자 스키마
│   │   ├── model.py    # ML 모델 스키마
│   │   ├── api_key.py  # API 키 스키마
│   │   ├── endpoint.py # 엔드포인트 스키마
│   │   └── inference.py # 추론 스키마
│   │
│   ├── services/       # 비즈니스 로직
│   │   ├── auth_service.py    # 인증 서비스
│   │   ├── model_service.py   # 모델 관리 서비스
│   │   ├── api_key_service.py # API 키 서비스
│   │   ├── endpoint_service.py # 엔드포인트 서비스
│   │   └── inference_service.py # 추론 서비스
│   │
│   ├── utils/          # 유틸리티
│   │   ├── file_handler.py  # 파일 처리
│   │   ├── model_loader.py  # 모델 로딩
│   │   └── validators.py    # 데이터 검증
│   │
│   └── main.py        # FastAPI 앱 진입점
│
├── worker/            # Celery 워커
│   ├── inference/     # 추론 엔진
│   │   ├── base_inference.py    # 기본 추론 인터페이스
│   │   ├── sklearn_inference.py # Scikit-learn 추론
│   │   └── text_inference.py    # 텍스트 모델 추론
│   │
│   ├── model_manager/ # 모델 관리자
│   │   ├── base_manager.py      # 기본 관리자 인터페이스
│   │   ├── pytorch_manager.py   # PyTorch 모델 관리
│   │   ├── sklearn_manager.py   # Scikit-learn 모델 관리
│   │   └── transformers_manager.py # Transformers 모델 관리
│   │
│   ├── utils/        # 유틸리티
│   │   ├── gpu_monitor.py    # GPU 모니터링
│   │   └── model_loader.py   # 모델 로딩
│   │
│   ├── celery_app.py # Celery 설정
│   ├── tasks.py      # Celery 태스크
│   └── debug_redis.py # Redis 디버깅 도구
│
├── frontend/         # 웹 인터페이스
│   ├── static/      # 정적 파일
│   ├── index.html   # 메인 페이지
│   ├── login.html   # 로그인
│   ├── register.html # 회원가입
│   ├── dashboard.html # 대시보드
│   ├── models.html  # 모델 관리
│   ├── api-keys.html # API 키 관리
│   ├── endpoints.html # 엔드포인트 관리
│   ├── inference.html # 추론 테스트
│   └── upload.html  # 모델 업로드
│
├── uploads/          # 업로드된 파일
│   └── models/      # 모델 파일 저장
│       └── user_{id}/ # 사용자별 모델 디렉토리
│
├── deploy/          # 배포 관련
│   ├── models/     # 예제 모델
│   └── train_iris_model.py # 예제 모델 학습
│
├── docker/         # Docker 설정
│   ├── worker.Dockerfile # 워커 이미지
│   └── docker-compose.worker.yaml # 워커 컴포즈
│
├── tests/          # 테스트 코드
├── scripts/        # 유틸리티 스크립트
│   ├── init_db.py  # DB 초기화
│   ├── create_admin.py # 관리자 생성
│   ├── start_worker.py # 워커 시작
│   └── start_beat.py  # 주기적 작업 시작
│
└── logs/           # 로그 파일
```

## 주요 컴포넌트 설명

### 1. 백엔드 (app/)
- **API (api/)**: RESTful API 엔드포인트 구현
  - 인증, 모델 관리, API 키, 엔드포인트, 추론 기능 제공
  - FastAPI 라우터를 통한 엔드포인트 정의
  - 의존성 주입을 통한 인증 및 권한 관리

- **핵심 설정 (core/)**
  - 환경 변수 및 설정 관리
  - JWT 기반 인증
  - Redis 연결 관리
  - FastAPI 의존성 정의

- **데이터베이스 (db/)**
  - SQLAlchemy 모델 정의
  - CRUD 작업 구현
  - 데이터베이스 연결 및 세션 관리

- **스키마 (schemas/)**
  - Pydantic 모델을 통한 데이터 검증
  - API 요청/응답 스키마 정의
  - 데이터 변환 및 직렬화

- **서비스 (services/)**
  - 비즈니스 로직 구현
  - 모델 관리 및 추론 처리
  - API 키 및 엔드포인트 관리

- **유틸리티 (utils/)**
  - 파일 업로드/다운로드 처리
  - 모델 로딩 및 검증
  - 데이터 검증 함수

### 2. 워커 (worker/)
- **추론 엔진 (inference/)**
  - 프레임워크별 추론 로직 구현
  - 비동기 추론 처리
  - 결과 캐싱

- **모델 관리자 (model_manager/)**
  - 프레임워크별 모델 로딩/언로딩
  - 메모리 관리
  - 모델 상태 추적

- **유틸리티 (utils/)**
  - GPU 리소스 모니터링
  - 모델 로딩 지원
  - 디버깅 도구

### 3. 프론트엔드 (frontend/)
- **HTML 템플릿**
  - 사용자 인증 (로그인/회원가입)
  - 모델 관리 인터페이스
  - API 키 관리
  - 엔드포인트 관리
  - 추론 테스트 인터페이스

### 4. 배포 (deploy/)
- **예제 모델**
  - Scikit-learn Iris 모델
  - 모델 학습 및 저장 스크립트

### 5. Docker (docker/)
- **워커 설정**
  - Celery 워커 컨테이너화
  - GPU 지원 설정
  - 환경 변수 관리

### 6. 스크립트 (scripts/)
- **유틸리티 스크립트**
  - 데이터베이스 초기화
  - 관리자 계정 생성
  - 워커 및 주기적 작업 시작

### 7. 파일 저장소 (uploads/)
- **모델 파일 저장**
  - 사용자별 디렉토리 구조 (`user_{id}/`)
  - 지원하는 파일 형식: `.h5`, `.pkl`, `.pt`, `.pth`, `.onnx`
  - 최대 파일 크기: 100MB
  - 자동 디렉토리 생성 및 관리
  - 파일 업로드 및 로컬 경로 지원

## 시작하기

### 환경 설정

1. `.env` 파일 생성
```bash
cp .env.template .env
```

2. 환경 변수 설정
- `DATABASE_URL`: 데이터베이스 연결 문자열
- `SECRET_KEY`: JWT 시크릿 키
- `REDIS_URL`: Redis 연결 문자열

### 설치 및 실행

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. 데이터베이스 초기화
```bash
python scripts/init_db.py
```

3. 서버 실행
```bash
uvicorn app.main:app --reload
```

4. 워커 실행
```bash
celery -A worker.celery_app worker --loglevel=debug --concurrency=1
```

5. 주기적 작업 실행
```bash
celery -A worker.celery_app beat
```

### Docker를 이용한 실행

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 주요 API 엔드포인트

### 인증
- `POST /auth/register`: 회원가입
- `POST /auth/login`: 로그인
- `GET /auth/me`: 현재 사용자 정보
- `PUT /auth/me`: 사용자 정보 수정

### 모델 관리
- `GET /models`: 모델 목록 조회
- `POST /models`: 모델 업로드 (name, type, framework, description, file/file_path)
- `GET /models/{model_id}`: 모델 상세 정보
- `DELETE /models/{model_id}`: 모델 삭제

### API 키 관리
- `GET /api-keys`: API 키 목록 조회
- `POST /api-keys`: API 키 생성
- `GET /api-keys/{api_key_id}`: API 키 상세 정보
- `DELETE /api-keys/{api_key_id}`: API 키 삭제

### 엔드포인트 관리
- `GET /endpoints`: 엔드포인트 목록 조회
- `POST /endpoints`: 엔드포인트 생성
- `GET /endpoints/{endpoint_id}`: 엔드포인트 상세 정보
- `PUT /endpoints/{endpoint_id}`: 엔드포인트 수정
- `DELETE /endpoints/{endpoint_id}`: 엔드포인트 삭제

### 추론
- `POST /inference/predict`: 추론 요청 제출
- `POST /inference/{endpoint_path}`: 엔드포인트를 통한 추론 요청 (API 키 인증 지원)
- `GET /inference/result/{task_id}`: 추론 결과 조회

## 지원하는 모델 프레임워크

### Scikit-learn
- 분류 모델
- 회귀 모델
- 특성 이름과 타겟 이름 지원

### PyTorch
- 이미지 분류 모델
- 텍스트 분류 모델
- GPU 가속 지원

### Transformers
- 텍스트 분류
- 텍스트 생성
- 토크나이저 자동 로딩

## 모니터링 및 관리

- GPU 리소스 모니터링
- 작업 큐 상태 확인
- 모델 메모리 사용량 추적
- 자동 모델 정리 (유휴 모델)

## 개발 도구

### Redis 디버깅
```bash
# Redis 큐 상태 확인
python -m worker.debug_redis

# Redis 데이터 초기화
python -m worker.debug_redis clear
```

## 라이선스

MIT License
