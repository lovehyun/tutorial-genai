# ML Serving Platform Worker

## 개요
ML Serving Platform의 Worker는 Celery를 기반으로 한 비동기 작업 처리 시스템입니다. 이 시스템은 ML 모델의 추론 요청을 처리하고, 모델의 생명주기를 관리하며, 시스템 리소스를 모니터링합니다.

## 디렉토리 구조
```
worker/
├── inference/              # 추론 엔진 관련 코드
│   ├── base_inference.py   # 기본 추론 엔진 인터페이스
│   ├── sklearn_inference.py # Scikit-learn 모델 추론 엔진
│   └── text_inference.py   # 텍스트 모델 추론 엔진
├── model_manager/          # 모델 관리자 관련 코드
│   ├── base_manager.py     # 기본 모델 관리자 인터페이스
│   ├── pytorch_manager.py  # PyTorch 모델 관리자
│   ├── sklearn_manager.py  # Scikit-learn 모델 관리자
│   └── transformers_manager.py # Transformers 모델 관리자
├── utils/                  # 유틸리티 함수들
│   ├── gpu_monitor.py      # GPU 리소스 모니터링
│   └── model_loader.py     # 모델 로딩 유틸리티
├── celery_app.py          # Celery 앱 설정
├── tasks.py               # Celery 태스크 정의
├── debug_redis.py         # Redis 디버깅 도구
└── main.py               # Worker 실행 진입점
```

## 주요 컴포넌트 설명

### 1. 추론 엔진 (inference/)
- **base_inference.py**: 모든 추론 엔진의 기본 인터페이스를 정의
- **sklearn_inference.py**: Scikit-learn 모델을 위한 추론 엔진
- **text_inference.py**: 텍스트 기반 모델(PyTorch, Transformers)을 위한 추론 엔진

### 2. 모델 관리자 (model_manager/)
- **base_manager.py**: 모든 모델 관리자의 기본 인터페이스 정의
- **pytorch_manager.py**: PyTorch 모델의 로딩, 추론, 메모리 관리
- **sklearn_manager.py**: Scikit-learn 모델의 로딩, 추론, 메모리 관리
- **transformers_manager.py**: Transformers 모델의 로딩, 추론, 메모리 관리

### 3. 유틸리티 (utils/)
- **gpu_monitor.py**: GPU 메모리 사용량 및 시스템 리소스 모니터링
- **model_loader.py**: 다양한 프레임워크의 모델 로딩 지원

### 4. 핵심 파일
- **celery_app.py**: Celery 워커 설정 및 구성
- **tasks.py**: 
  - `process_inference`: ML 추론 요청 처리
  - `cleanup_models`: 유휴 모델 정리
  - `health_check`: 워커 상태 확인
- **debug_redis.py**: Redis 작업 큐 디버깅 도구
- **main.py**: 워커 실행을 위한 진입점

## 주요 기능

### 1. 모델 추론 처리
- 다양한 ML 프레임워크(Scikit-learn, PyTorch, Transformers) 지원
- 비동기 추론 요청 처리
- 결과 캐싱 및 상태 관리

### 2. 모델 생명주기 관리
- 모델 로딩 및 언로딩
- 메모리 사용량 최적화
- 유휴 모델 자동 정리

### 3. 리소스 모니터링
- GPU 메모리 사용량 추적
- 시스템 리소스 모니터링
- 워커 상태 확인

### 4. 오류 처리 및 재시도
- 추론 실패 시 자동 재시도
- 상세한 오류 로깅
- Redis를 통한 작업 상태 관리

## 실행 방법
```bash
# 워커 실행
celery -A worker.celery_app worker --loglevel=debug --concurrency=1

# 주기적 작업 실행 (cleanup, health check)
celery -A worker.celery_app beat
```

## Redis 디버깅 도구 사용법

### 1. 기본 사용법
```bash
# Redis 큐 상태 확인
python -m worker.debug_redis

# Redis 데이터 초기화
python -m worker.debug_redis clear
```

### 2. 주요 기능
- **Redis 큐 상태 확인**
  - Redis 연결 상태 확인
  - Celery 설정 확인 (Broker URL, Result Backend)
  - inference_tasks 큐 상태 및 대기 중인 작업 확인
  - 작업 상태 및 결과 확인

- **Redis 데이터 초기화**
  - inference_tasks 큐 초기화
  - 작업 상태 데이터 초기화
  - 작업 결과 데이터 초기화

### 3. 주의사항
- 디버깅 도구는 개발 환경에서만 사용
- `clear` 명령어는 모든 Redis 데이터를 삭제하므로 주의해서 사용
- Redis 연결 정보는 환경 변수에서 자동으로 로드

## 주의사항
1. 모델 파일은 반드시 지정된 형식으로 저장되어야 함
2. 각 프레임워크별 모델 관리자는 해당 프레임워크의 특성을 고려하여 구현됨
3. 메모리 관리를 위해 주기적인 모델 정리가 필요함
