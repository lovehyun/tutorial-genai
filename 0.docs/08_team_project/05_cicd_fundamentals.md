# CI/CD 기초

> 코드를 작성하는 것보다 그 코드가 실제로 동작하는지 빠르게 확인하고, 안전하게 배포하는 것이 더 중요합니다. CI/CD는 코드 변경이 발생할 때마다 자동으로 빌드·테스트·배포를 수행하여 팀이 빠르게 피드백을 받고, 언제든지 신뢰할 수 있는 소프트웨어를 배포할 수 있게 하는 핵심 개발 문화입니다.

---

## 1. CI/CD 개요

### 지속적 통합(CI: Continuous Integration)의 정의와 목표

**지속적 통합(Continuous Integration)**은 팀원들이 각자 작업한 코드를 하루에도 여러 번 공유 브랜치에 통합하고, 통합할 때마다 자동으로 빌드와 테스트를 실행하는 개발 방법론입니다. 1990년대 Extreme Programming(XP) 커뮤니티에서 시작된 개념으로, 현재는 모든 현대 소프트웨어 개발팀의 표준 관행이 되었습니다.

CI의 핵심 철학은 **"통합의 고통을 줄이려면 더 자주 통합하라"**는 역설적인 원칙에서 출발합니다. 코드를 오랫동안 분기(branch)에만 가두어 두면, 나중에 메인 브랜치에 합칠 때 수많은 충돌과 오류가 한꺼번에 터집니다. 반면 매일 작은 변경을 통합하면 충돌이 작고, 원인을 찾기 쉽고, 수정이 빠릅니다.

**CI가 달성하고자 하는 목표:**

- **빠른 피드백**: 코드를 푸시하면 10분 이내에 버그가 있는지 알 수 있습니다
- **통합 문제 조기 발견**: 여러 팀원의 코드가 서로 충돌하는 문제를 즉시 감지합니다
- **항상 동작하는 메인 브랜치**: main 브랜치는 언제나 빌드되고 테스트를 통과한 상태를 유지합니다
- **자동화된 품질 검사**: 사람이 수동으로 하던 코드 리뷰 전 기본 검사를 자동화합니다

### 지속적 전달(Continuous Delivery) vs 지속적 배포(Continuous Deployment)

CI 다음 단계로 두 가지 개념이 있습니다. 이름이 비슷하여 혼동하기 쉽지만 결정적인 차이가 있습니다.

| 구분 | 지속적 전달 (Continuous Delivery) | 지속적 배포 (Continuous Deployment) |
|------|----------------------------------|--------------------------------------|
| **약자** | CD (Delivery) | CD (Deployment) |
| **정의** | 언제든지 배포 가능한 상태를 유지, 실제 배포는 **수동 승인** | 모든 테스트 통과 시 **자동으로 프로덕션** 배포 |
| **프로덕션 배포** | 사람이 버튼을 눌러 배포 | 파이프라인이 자동으로 배포 |
| **승인 단계** | 있음 (QA, PM 승인 게이트) | 없음 또는 자동화된 게이트 |
| **적합한 상황** | 배포 시점을 제어해야 하는 서비스 (금융, 의료) | 빠른 이터레이션이 필요한 웹 서비스 |
| **예시 기업** | 은행 앱, 기업용 SaaS | Netflix, Amazon, Facebook |
| **리스크** | 낮음 (검증된 버전만 배포) | 높음 (버그가 즉시 프로덕션 노출) |

> **핵심 포인트:** CI/CD에서 CD는 두 가지 의미를 모두 포함합니다. 팀 프로젝트에서는 스테이징까지는 자동 배포(Continuous Deployment), 프로덕션은 수동 승인(Continuous Delivery)을 권장합니다. 이것이 현업에서 가장 많이 사용하는 하이브리드 방식입니다.

### DevOps 문화와의 연결

CI/CD는 단순히 도구나 기술이 아니라 **DevOps 문화의 핵심 실천법**입니다. DevOps는 개발(Development)과 운영(Operations) 팀 사이의 장벽을 허물고, 소프트웨어를 더 빠르고 안정적으로 제공하기 위한 문화·철학·방법론의 집합입니다.

```mermaid
graph LR
    Dev["개발팀\n(Dev)"]:::blue
    Ops["운영팀\n(Ops)"]:::orange
    CICD["CI/CD 파이프라인\n(자동화 다리)"]:::purple
    Quality["품질 보증\n코드 리뷰 + 테스트"]:::green
    Feedback["빠른 피드백\n모니터링 + 알림"]:::yellow

    Dev -->|코드 푸시| CICD
    CICD -->|자동 빌드·테스트| Quality
    Quality -->|승인 후 배포| Ops
    Ops -->|운영 데이터| Feedback
    Feedback -->|개선 사항| Dev

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
```

전통적인 개발 방식에서는 개발팀이 몇 달에 걸쳐 기능을 만들고, 운영팀에 "배포해 주세요"라는 두꺼운 문서와 함께 소프트웨어를 넘겼습니다. 이 과정에서 "내 컴퓨터에서는 됐는데"라는 말이 수없이 등장했습니다. CI/CD는 이 장벽을 자동화된 파이프라인으로 대체합니다.

### CI/CD가 없을 때 vs 있을 때 비교

| 항목 | CI/CD 없음 | CI/CD 있음 |
|------|-----------|-----------|
| **통합 주기** | 수주~수개월에 한 번 | 하루에도 수십 번 |
| **배포 주기** | 월 1~2회 대규모 배포 | 하루 수회 소규모 배포 |
| **버그 발견 시점** | 배포 직전 또는 배포 후 사용자 보고 | 코드 푸시 후 수분 내 |
| **배포 소요 시간** | 수 시간 (수동 절차 포함) | 수십 분 (자동화) |
| **롤백 방법** | 수동으로 이전 코드 복원 | 버튼 클릭 또는 자동 롤백 |
| **야근 빈도** | 배포일 야근 필수 | 배포일이 평일과 동일 |
| **팀원 스트레스** | 배포 전 극심한 긴장 | 배포가 일상적인 작업 |
| **코드 리뷰 품질** | 기본 오류도 놓치는 경우 다수 | 자동화 검사 후 핵심 로직 집중 리뷰 |
| **문서화 수준** | 배포 절차서가 비공식 문서 | 파이프라인 자체가 실행 가능한 문서 |

---

## 2. CI 파이프라인

### CI 파이프라인 전체 흐름

CI 파이프라인은 개발자가 코드를 푸시하는 순간부터 빌드 아티팩트(배포 가능한 산출물)가 생성되기까지의 전 과정을 자동화합니다. 각 단계는 이전 단계가 성공해야만 다음 단계로 진행됩니다.

```mermaid
graph TD
    Push["코드 푸시"]:::purple
    Trigger["CI 트리거"]:::gray
    Setup["체크아웃 + 의존성 설치"]:::blue
    Lint["린트 검사"]:::orange
    Test["단위/통합 테스트"]:::orange
    Build["빌드 + 아티팩트 저장"]:::green
    Notify["결과 알림"]:::yellow

    Push --> Trigger --> Setup --> Lint
    Lint -->|"통과"| Test
    Lint -->|"실패"| Notify
    Test -->|"통과"| Build
    Test -->|"실패"| Notify
    Build --> Notify

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    classDef gray fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 각 단계 상세 설명

#### 1단계: 코드 체크아웃 (Code Checkout)

CI 서버(GitHub Actions Runner 등)는 원격 저장소의 최신 커밋을 워킹 디렉토리로 내려받습니다. 이 시점에서 "어떤 브랜치의 어떤 커밋"을 테스트할 것인지가 결정됩니다.

```yaml
# GitHub Actions에서의 체크아웃
- name: 코드 체크아웃
  uses: actions/checkout@v4
  with:
    fetch-depth: 0  # 전체 히스토리 (커버리지 비교 시 필요)
```

#### 2단계: 의존성 설치 (Dependency Installation)

`requirements.txt`나 `package.json`에 명시된 라이브러리를 설치합니다. 캐싱을 활용하면 이 단계의 실행 시간을 대폭 줄일 수 있습니다. 의존성 설치 실패는 잘못된 버전 명시나 패키지 저장소 접근 문제를 의미합니다.

```yaml
- name: Python 의존성 캐시
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

- name: 의존성 설치
  run: pip install -r requirements.txt -r requirements-dev.txt
```

#### 3단계: 린트 검사 (Lint)

코드가 팀에서 정한 스타일 규칙을 따르는지, 잠재적 오류 패턴이 없는지 정적으로 분석합니다. 실제 코드를 실행하지 않고도 버그를 찾을 수 있습니다.

```bash
# Python 린트 실행
ruff check .          # 코드 품질 검사
ruff format --check . # 포매팅 검사 (수정하지 않고 확인만)
mypy app/             # 타입 검사
```

#### 4단계: 단위 테스트 (Unit Test)

개별 함수나 클래스가 의도대로 동작하는지 검증합니다. 외부 의존성(데이터베이스, 외부 API)은 모킹(mocking)으로 대체합니다. 단위 테스트는 빠르게 실행되어야 합니다(전체 5분 이내).

```bash
# pytest 실행 (커버리지 포함)
pytest tests/unit/ \
  --cov=app \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -v
```

#### 5단계: 통합 테스트 (Integration Test)

실제 데이터베이스, 외부 API, 메시지 큐 등을 연결하여 컴포넌트 간 상호작용이 올바른지 검증합니다. Docker Compose로 의존 서비스(PostgreSQL, Redis 등)를 띄운 후 테스트를 실행합니다.

```bash
# docker-compose로 테스트 환경 구성 후 실행
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/ -v
docker-compose -f docker-compose.test.yml down
```

#### 6단계: 빌드 (Build)

테스트를 통과한 코드로 배포 가능한 산출물을 만듭니다. Python 백엔드라면 Docker 이미지, React 프론트엔드라면 정적 빌드 파일이 됩니다.

```bash
# Docker 이미지 빌드 (GitHub SHA를 태그로 사용)
docker build \
  -t myapp:${{ github.sha }} \
  -t myapp:latest \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  .
```

#### 7단계: 아티팩트 저장 (Artifact Storage)

빌드된 Docker 이미지를 컨테이너 레지스트리(Docker Hub, AWS ECR, GitHub Container Registry)에 푸시합니다. 이 이미지가 이후 CD 파이프라인에서 실제 서버에 배포됩니다.

```bash
# AWS ECR에 이미지 푸시
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY
docker push $ECR_REGISTRY/myapp:${{ github.sha }}
```

### 빠른 피드백의 중요성

CI 파이프라인의 생명은 **속도**입니다. 파이프라인이 30분 이상 걸린다면 개발자는 다른 작업으로 컨텍스트 전환을 했다가 돌아와야 합니다. 이상적인 CI 완료 시간은 **10분 이내**입니다.

| 파이프라인 시간 | 개발자 경험 | 권장 여부 |
|--------------|-----------|---------|
| 5분 이내 | 커피 한 잔 기다리는 수준, 즉각 대응 가능 | 최고 |
| 5~10분 | 짧은 다른 작업 가능, 여전히 빠른 피드백 | 적절 |
| 10~20분 | 컨텍스트 전환 발생, 집중력 분산 | 개선 필요 |
| 20~30분 | 개발자가 파이프라인 확인을 잊음 | 비권장 |
| 30분 이상 | 파이프라인을 무시하기 시작 | 심각한 문제 |

파이프라인 속도를 높이는 방법:
- **병렬 실행**: 린트와 단위 테스트를 동시에 실행
- **캐싱**: 의존성 캐시로 설치 시간 단축
- **경량 Docker 이미지**: 빌드 캐시 레이어 최적화
- **테스트 분할**: 느린 통합 테스트는 별도 워크플로우로 분리

### CI 실패 시 대응 절차

```
CI 실패 발생
    │
    ├── 1. 실패 알림 확인 (Slack / GitHub PR 코멘트)
    │
    ├── 2. 실패 단계 파악 (린트? 단위 테스트? 빌드?)
    │
    ├── 3. 로그 확인 (GitHub Actions 로그 탭)
    │
    ├── 4. 로컬에서 동일 명령어 재현
    │       $ ruff check .
    │       $ pytest tests/unit/ -v
    │
    ├── 5. 수정 후 커밋 푸시 → CI 자동 재실행
    │
    └── 6. 모든 단계 통과 확인 후 PR 리뷰 요청
```

> **핵심 포인트:** CI가 실패한 상태에서 PR을 머지하지 마세요. "일단 머지하고 나중에 고치겠다"는 접근은 팀 전체의 main 브랜치를 망가뜨립니다. CI 통과를 PR 머지의 필수 조건(Required Status Check)으로 설정하면 이를 강제할 수 있습니다.

---

## 3. CD 파이프라인

### CD 파이프라인 전체 흐름

CD 파이프라인은 CI가 생성한 아티팩트(Docker 이미지)를 실제 서버에 배포하는 과정을 자동화합니다. 스테이징(Staging) 환경 배포 후 사람이나 자동화된 검사가 승인하면 프로덕션(Production)에 배포합니다.

```mermaid
graph TD
    Artifact["검증된 아티팩트\nDocker Image: myapp:abc1234"]:::purple
    StagingDeploy["스테이징 배포\nECS / Kubernetes 업데이트\n(자동 실행)"]:::blue
    SmokeTest1["스테이징 스모크 테스트\n헬스체크 엔드포인트 확인\n기본 시나리오 E2E 테스트"]:::blue
    ApprovalGate["승인 게이트\nPM / QA 팀 검토\n(수동 승인 또는 자동화)"]:::yellow
    ProdDeploy["프로덕션 배포\n배포 전략 선택:\nRolling / Blue-Green / Canary"]:::green
    SmokeTest2["프로덕션 스모크 테스트\n실제 트래픽 정상 여부 확인\n에러율 · 응답시간 모니터링"]:::green
    Rollback["롤백 실행\n이전 버전으로 즉시 복구\n원인 분석 후 재배포"]:::orange
    Done["배포 완료\n팀 알림 발송\n배포 로그 기록"]:::gray

    Artifact --> StagingDeploy
    StagingDeploy --> SmokeTest1
    SmokeTest1 -->|통과| ApprovalGate
    SmokeTest1 -->|실패| Rollback
    ApprovalGate -->|승인| ProdDeploy
    ApprovalGate -->|거부| Rollback
    ProdDeploy --> SmokeTest2
    SmokeTest2 -->|정상| Done
    SmokeTest2 -->|이상 감지| Rollback
    Rollback -->|원인 수정 후| Artifact

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    classDef gray fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 배포 전략 복습 (07 모듈 연계)

07 모듈(배포 아키텍처)에서 학습한 배포 전략을 CD 파이프라인에 어떻게 적용하는지 정리합니다.

| 배포 전략 | 동작 방식 | 장점 | 단점 | 적합한 상황 |
|----------|---------|------|------|------------|
| **Rolling Update** | 인스턴스를 순차적으로 교체 (구버전 → 신버전) | 간단, 추가 인프라 불필요 | 배포 중 양쪽 버전 혼재, 롤백 느림 | 소규모 서비스, 호환성 있는 변경 |
| **Blue-Green** | 구버전(Blue)과 신버전(Green)을 동시에 유지, 트래픽을 한 번에 전환 | 즉각 롤백, 배포 위험 최소화 | 인프라 2배 비용, 설정 복잡 | 중요 서비스, 즉각 롤백 필수 |
| **Canary** | 신버전으로 트래픽을 5% → 10% → 50% → 100% 단계적으로 증가 | 실제 사용자로 리스크 검증, 점진적 배포 | 복잡한 모니터링 필요, 버전 관리 어려움 | 대규모 서비스, A/B 테스트 병행 |

**팀 프로젝트 권장 전략:**

초기 팀 프로젝트에서는 Blue-Green 배포를 권장합니다. AWS ECS에서는 `aws ecs update-service` 명령어와 로드밸런서 타겟 그룹 전환으로 구현할 수 있으며, 문제 발생 시 즉시 이전 버전으로 복구가 가능합니다.

### 롤백 전략

배포 후 문제가 발생했을 때의 롤백 전략은 배포 전략 만큼 중요합니다. **"언제 롤백할 것인가"**의 기준을 사전에 정해두어야 합니다.

**자동 롤백 트리거 조건:**
- 헬스체크 엔드포인트 연속 3회 실패
- 5xx 에러율이 배포 전 대비 2배 이상 증가
- 평균 응답 시간이 3초 초과
- 스모크 테스트 실패

```yaml
# AWS ECS 이전 태스크 정의로 롤백
aws ecs update-service \
  --cluster production \
  --service myapp-service \
  --task-definition myapp:PREVIOUS_VERSION \
  --force-new-deployment
```

**수동 롤백 절차:**

```
1. 장애 감지 (모니터링 알림)
2. 인시던트 채널 개설 (Slack #incident-YYYYMMDD)
3. 롤백 결정 (팀 리더 승인)
4. 이전 버전 아티팩트 태그 확인
5. 롤백 명령어 실행
6. 서비스 정상화 확인 (헬스체크 + 주요 기능 테스트)
7. 장애 원인 분석 및 포스트모텀 작성
```

### 환경별 배포 승인 정책

| 환경 | 배포 트리거 | 승인 주체 | 롤백 방법 |
|------|-----------|---------|---------|
| **개발(Dev)** | feature 브랜치 푸시 시 자동 | 자동 (승인 없음) | 새 브랜치로 대체 |
| **스테이징(Staging)** | main 브랜치 머지 시 자동 | CI 통과 시 자동 | 이전 이미지 재배포 |
| **프로덕션(Production)** | 수동 트리거 (릴리스 태그 생성) | PM 또는 팀 리더 | Blue-Green 즉시 전환 |

---

## 4. 테스트 자동화

### 테스트 피라미드

테스트 피라미드는 어떤 종류의 테스트를 얼마나 작성해야 하는지를 시각적으로 보여주는 가이드입니다. 피라미드의 아래로 갈수록 테스트 수가 많고, 실행 속도가 빠르며, 작성 비용이 낮습니다.

```mermaid
graph TB
    E2E["E2E 테스트 (10%)\nSelenium / Playwright\n실제 브라우저에서 사용자 시나리오 전체 검증\n느림 · 비용 높음 · 유지보수 어려움"]:::orange
    Integration["통합 테스트 (20%)\npytest + testcontainers\nDB · API · 메시지큐 간 연동 검증\n중간 속도 · 중간 비용"]:::blue
    Unit["단위 테스트 (70%)\npytest + unittest.mock\n개별 함수·클래스 동작 검증\n빠름 · 비용 낮음 · 유지보수 쉬움"]:::green

    E2E --> Integration
    Integration --> Unit

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
```

**피라미드를 역삼각형으로 만들면 안 되는 이유:**

E2E 테스트에만 의존하면 실행 시간이 수 시간이 걸리고, 테스트가 실패했을 때 어느 계층에서 문제가 발생했는지 알 수 없습니다. 또한 UI 변경 한 번으로 수백 개의 테스트가 깨질 수 있습니다.

### pytest 기본 사용법

pytest는 Python의 표준 테스트 프레임워크입니다. 간결한 문법과 강력한 플러그인 생태계로 단위 테스트부터 통합 테스트까지 커버합니다.

**기본 테스트 작성:**

```python
# tests/unit/test_calculator.py
def test_add_two_numbers():
    """두 수를 더하는 기본 테스트"""
    result = add(2, 3)
    assert result == 5

def test_add_negative_numbers():
    """음수 덧셈 테스트"""
    result = add(-1, -1)
    assert result == -2

def test_divide_by_zero_raises_error():
    """0으로 나누기 시 예외 발생 확인"""
    import pytest
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

**fixtures 활용:**

`fixture`는 테스트에 필요한 사전 조건이나 공통 데이터를 재사용 가능하게 만드는 기능입니다.

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

@pytest.fixture(scope="session")
def test_engine():
    """테스트용 인메모리 SQLite 데이터베이스 엔진 생성"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_engine):
    """각 테스트마다 독립적인 DB 세션 제공 (롤백으로 격리)"""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user():
    """테스트용 사용자 데이터"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user"
    }
```

**parametrize로 다양한 입력 테스트:**

```python
# tests/unit/test_validator.py
import pytest
from app.validators import validate_email

@pytest.mark.parametrize("email, expected", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("user@", False),
    ("@example.com", False),
    ("user+tag@example.co.kr", True),
    ("", False),
    (None, False),
])
def test_email_validation(email, expected):
    """다양한 이메일 형식에 대한 유효성 검사"""
    assert validate_email(email) == expected
```

**conftest.py 구조:**

`conftest.py`는 pytest가 자동으로 인식하는 설정 파일로, 디렉토리 레벨에 따라 범위가 결정됩니다.

```
tests/
├── conftest.py              # 전체 테스트 공통 fixture (DB 엔진, 앱 클라이언트)
├── unit/
│   ├── conftest.py          # 단위 테스트 전용 fixture (mock 객체)
│   ├── test_user_service.py
│   └── test_ai_service.py
└── integration/
    ├── conftest.py          # 통합 테스트 전용 fixture (실제 DB 연결)
    ├── test_user_api.py
    └── test_ai_api.py
```

### 테스트 커버리지

**커버리지(Coverage)**는 테스트가 소스 코드의 몇 퍼센트를 실행했는지 측정하는 지표입니다. 100%가 목표가 아니라, **80% 이상**을 유지하면서 핵심 비즈니스 로직에 집중하는 것이 중요합니다.

```bash
# pytest-cov 설치
pip install pytest-cov

# 커버리지 측정 및 HTML 리포트 생성
pytest tests/ \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-fail-under=80

# 결과 예시:
# Name                    Stmts   Miss  Cover
# -------------------------------------------
# app/main.py                45      2    96%
# app/services/user.py       78     12    85%
# app/services/ai.py         62      8    87%
# -------------------------------------------
# TOTAL                     185     22    88%
```

**pytest.ini 또는 pyproject.toml 설정:**

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
    "-v",
]

[tool.coverage.run]
omit = [
    "tests/*",
    "app/migrations/*",
    "app/main.py",  # FastAPI 진입점
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

### AI 서비스 테스트 전략

AI 서비스(LLM API 호출, 임베딩 생성 등)는 일반 비즈니스 로직과 다른 테스트 전략이 필요합니다. 실제 API를 테스트에서 매번 호출하면 비용이 발생하고, 네트워크 의존성으로 인해 테스트가 불안정해집니다.

**API 모킹 (unittest.mock 활용):**

```python
# tests/unit/test_ai_service.py
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.ai_service import summarize_text

@pytest.mark.asyncio
async def test_summarize_text_success():
    """OpenAI API 호출을 모킹하여 요약 서비스 테스트"""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="이것은 테스트 요약입니다."))
    ]

    with patch("app.services.ai_service.openai_client.chat.completions.create",
               new_callable=AsyncMock, return_value=mock_response):
        result = await summarize_text("긴 텍스트 내용...")

    assert result == "이것은 테스트 요약입니다."
    assert len(result) > 0

@pytest.mark.asyncio
async def test_summarize_text_api_error():
    """API 오류 발생 시 적절한 예외 처리 확인"""
    from openai import APIError
    import httpx

    with patch("app.services.ai_service.openai_client.chat.completions.create",
               new_callable=AsyncMock,
               side_effect=APIError("API 오류", request=MagicMock(), body=None)):
        with pytest.raises(ValueError, match="AI 서비스 오류"):
            await summarize_text("텍스트")
```

**임베딩 결과 검증:**

```python
# tests/unit/test_embedding_service.py
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.embedding_service import get_embedding, cosine_similarity

def test_embedding_dimension():
    """임베딩 벡터 차원 수 검증 (text-embedding-3-small: 1536차원)"""
    mock_embedding = [0.1] * 1536  # 1536차원 임베딩

    with patch("app.services.embedding_service.openai_client.embeddings.create") as mock_create:
        mock_create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)]
        )
        result = get_embedding("테스트 문장")

    assert len(result) == 1536
    assert isinstance(result, list)

def test_cosine_similarity_identical_vectors():
    """동일한 벡터의 코사인 유사도는 1.0이어야 함"""
    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)

def test_cosine_similarity_orthogonal_vectors():
    """직교 벡터의 코사인 유사도는 0.0이어야 함"""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    assert cosine_similarity(vec1, vec2) == pytest.approx(0.0)

@pytest.fixture
def mock_embeddings():
    """테스트용 미리 계산된 임베딩 데이터"""
    return {
        "python": np.random.rand(1536).tolist(),
        "java": np.random.rand(1536).tolist(),
    }
```

> **핵심 포인트:** AI 서비스 테스트에서 실제 API를 호출하는 테스트는 `@pytest.mark.integration`으로 분리하고, 비용이 발생하는 테스트는 CI 파이프라인에서 선택적으로 실행합니다. 단위 테스트는 반드시 모킹을 사용하여 비용 없이 빠르게 실행되어야 합니다.

---

## 5. 코드 품질 도구

### Python 린터 도구

코드 품질 도구는 사람이 코드 리뷰에서 놓칠 수 있는 기계적인 오류(들여쓰기 불일치, 미사용 변수, 타입 오류 등)를 자동으로 검출합니다.

| 도구 | 역할 | 특징 | 속도 |
|------|------|------|------|
| **Ruff** | 린트 + 포매팅 | Rust로 작성, 기존 도구보다 10~100배 빠름, Black·isort·flake8 대체 가능 | 매우 빠름 |
| **Black** | 코드 포매팅 | 타협 없는 단일 스타일, 설정 최소화 ("The uncompromising code formatter") | 빠름 |
| **MyPy** | 정적 타입 검사 | Python 타입 힌트 기반으로 런타임 전 타입 오류 검출 | 느림 (대규모 프로젝트) |
| **Flake8** | 린트 | PEP 8 준수 검사, 플러그인 풍부 (Ruff로 대체 권장) | 보통 |

**Ruff 설정 예시 (`pyproject.toml`):**

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # 줄 길이 (Black이 처리)
    "B008",  # FastAPI Depends() 패턴 허용
]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**MyPy 설정 예시:**

```toml
[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true
disallow_untyped_defs = true  # 함수 타입 힌트 필수
warn_return_any = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false  # 테스트 코드는 완화
```

### JavaScript 품질 도구

| 도구 | 역할 | 특징 |
|------|------|------|
| **ESLint** | 린트 | JavaScript/TypeScript 코드 품질 검사, React 플러그인 지원 |
| **Prettier** | 포매팅 | 코드 스타일 자동 정리, ESLint와 함께 사용 |
| **TypeScript** | 타입 검사 | 정적 타입으로 런타임 오류 사전 방지 |

```json
// .eslintrc.json (React 프로젝트)
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn",
    "react/prop-types": "off"
  }
}
```

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 88,
  "tabWidth": 2
}
```

### SonarQube 소개

**SonarQube**는 코드 품질과 보안을 종합적으로 분석하는 플랫폼입니다. 단순한 린터를 넘어 **기술 부채(Technical Debt)**를 정량적으로 측정하고 관리할 수 있게 합니다.

SonarQube가 제공하는 분석 항목:

| 항목 | 설명 | 예시 |
|------|------|------|
| **버그(Bugs)** | 런타임 오류를 일으킬 가능성이 있는 코드 | NullPointerException 가능성 |
| **취약점(Vulnerabilities)** | 보안 위협이 될 수 있는 코드 | SQL 인젝션, 하드코딩된 비밀번호 |
| **코드 스멜(Code Smells)** | 즉각적 오류는 아니지만 유지보수를 어렵게 하는 코드 | 함수가 너무 길거나, 중복 코드 |
| **기술 부채(Technical Debt)** | 코드 스멜을 모두 수정하는 데 걸리는 예상 시간 | "현재 기술 부채: 3일 4시간" |
| **커버리지(Coverage)** | 테스트 커버리지 트렌드 | 커밋별 커버리지 변화 추적 |

**팀 프로젝트에서의 SonarQube:** SonarCloud(SaaS 버전)는 오픈소스 프로젝트에 무료로 제공됩니다. GitHub Actions와 통합하면 PR마다 코드 품질 리포트를 자동으로 받을 수 있습니다.

### pre-commit hooks 설정

**pre-commit**은 `git commit` 명령어를 실행하기 전에 자동으로 코드 검사를 실행하는 도구입니다. 나쁜 코드가 저장소에 커밋되기 전에 차단합니다.

```bash
# pre-commit 설치
pip install pre-commit

# .pre-commit-config.yaml 작성 후 훅 설치
pre-commit install

# 모든 파일에 수동 실행 (최초 설정 시)
pre-commit run --all-files
```

**`.pre-commit-config.yaml` 예시:**

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff: 린트 + 포매팅 (Python)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]        # 자동 수정 가능한 항목은 자동 수정
      - id: ruff-format      # 코드 포매팅

  # MyPy: 타입 검사 (Python)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-PyYAML

  # 일반적인 파일 검사
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace    # 줄 끝 공백 제거
      - id: end-of-file-fixer      # 파일 끝 개행 추가
      - id: check-yaml             # YAML 문법 검사
      - id: check-json             # JSON 문법 검사
      - id: check-toml             # TOML 문법 검사
      - id: check-merge-conflict   # 머지 충돌 마커 검사
      - id: check-added-large-files  # 대용량 파일 커밋 방지 (기본 500KB)
        args: ['--maxkb=1000']
      - id: detect-private-key     # 개인키/비밀키 커밋 방지

  # Prettier: 포매팅 (JavaScript/TypeScript)
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        types_or: [javascript, jsx, typescript, tsx, css, json, yaml, markdown]

  # ESLint: 린트 (JavaScript/TypeScript)
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.3.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
        additional_dependencies:
          - eslint@9.3.0
          - eslint-plugin-react@7.34.2
```

**pre-commit 동작 흐름:**

```
git commit -m "feat: 사용자 API 추가"
       │
       ▼
[pre-commit 실행]
  ✓ ruff (린트 검사)
  ✓ ruff-format (포매팅)
  ✗ mypy (타입 오류 발견!)
       │
       ▼
[커밋 차단] 타입 오류를 수정한 후 다시 커밋
```

> **핵심 포인트:** pre-commit은 로컬 개발 환경에서의 1차 방어선이고, CI 파이프라인은 2차 방어선입니다. 두 계층이 모두 있어야 코드 품질을 확실하게 보장할 수 있습니다. pre-commit이 없으면 CI 실패가 잦아지고, CI가 없으면 pre-commit을 우회할 수 있습니다.

---

## 6. 환경 관리

### 개발/스테이징/프로덕션 환경 분리

소프트웨어는 하나의 환경에서만 동작하지 않습니다. 개발자 로컬 환경, QA 검증 환경, 실제 사용자 환경은 서로 격리되어야 합니다.

| 환경 | 목적 | 데이터 | 외부 API | 인프라 규모 |
|------|------|--------|----------|-----------|
| **Development (Dev)** | 기능 개발 및 개인 테스트 | 가상 데이터, 자주 초기화 | Sandbox/Mock API | 로컬 또는 최소 사양 |
| **Staging** | 통합 테스트, QA 검증, 데모 | 프로덕션과 유사한 익명화 데이터 | 실제 API (별도 계정) | 프로덕션의 50~100% |
| **Production (Prod)** | 실제 사용자 서비스 | 실제 사용자 데이터 | 실제 API | 최대 사양 + 오토스케일링 |

**중요 원칙:**

- 스테이징 환경은 프로덕션과 **가능한 한 동일하게** 유지합니다
- 스테이징에서 통과하지 못한 변경은 절대 프로덕션에 배포하지 않습니다
- 각 환경은 독립된 데이터베이스, 독립된 Secrets를 사용합니다

### 환경변수 관리

**환경변수(Environment Variables)**는 코드 외부에서 설정을 주입하는 방법입니다. API 키, 데이터베이스 URL 같은 민감한 정보나 환경별로 달라지는 설정을 코드에 하드코딩하지 않고 환경변수로 관리합니다.

**`.env` 파일 구조 예시:**

```bash
# .env.example  (저장소에 커밋하는 템플릿 파일 - 실제 값 없음)
# 이 파일을 복사하여 .env로 만들고 실제 값을 채우세요.
# .env 파일은 절대 git에 커밋하지 마세요!

# ===== 애플리케이션 설정 =====
APP_ENV=development              # development | staging | production
APP_SECRET_KEY=your-secret-key-here
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG              # DEBUG | INFO | WARNING | ERROR

# ===== 데이터베이스 =====
DATABASE_URL=postgresql://user:password@localhost:5432/myapp_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# ===== Redis / 캐시 =====
REDIS_URL=redis://localhost:6379/0

# ===== AI API 키 =====
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_MODEL=text-embedding-3-small

# ===== AWS =====
AWS_REGION=ap-northeast-2
AWS_S3_BUCKET=myapp-dev-bucket
# AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY는 IAM Role 사용 권장

# ===== 외부 서비스 =====
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=app-password-here
```

**python-dotenv로 환경변수 로드:**

```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정 클래스 (타입 안전)"""

    # 애플리케이션
    app_env: str = "development"
    app_secret_key: str
    app_debug: bool = False
    app_log_level: str = "INFO"

    # 데이터베이스
    database_url: str
    database_pool_size: int = 5

    # AI API
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # AWS
    aws_region: str = "ap-northeast-2"
    aws_s3_bucket: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 (캐싱으로 반복 파일 읽기 방지)"""
    return Settings()

# FastAPI 의존성 주입
# def some_endpoint(settings: Settings = Depends(get_settings)):
#     ...
```

### Secrets 관리

API 키, 비밀번호 같은 민감한 정보는 `.env` 파일로도 충분하지 않습니다. CI/CD 파이프라인과 클라우드 환경에서는 전용 Secrets 관리 서비스를 사용합니다.

**GitHub Secrets:**

```yaml
# GitHub Actions에서 Secrets 사용
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: 배포 환경 구성
        env:
          # GitHub Repository Settings > Secrets에 등록된 값
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          echo "배포 환경 설정 완료"
          # 실제 값은 로그에 절대 출력되지 않음 (마스킹 처리)
```

**AWS Secrets Manager:**

프로덕션 환경에서는 GitHub Secrets보다 AWS Secrets Manager를 권장합니다. 자동 로테이션, 접근 감사 로그, 세밀한 IAM 권한 제어가 가능합니다.

```python
# app/utils/secrets.py
import boto3
import json
from functools import lru_cache

@lru_cache()
def get_secret(secret_name: str, region: str = "ap-northeast-2") -> dict:
    """AWS Secrets Manager에서 비밀값 조회"""
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# 사용 예시
# secrets = get_secret("myapp/production/api-keys")
# openai_key = secrets["OPENAI_API_KEY"]
```

| 방법 | 적합한 환경 | 장점 | 단점 |
|------|-----------|------|------|
| `.env` 파일 | 로컬 개발 | 간편, 빠른 설정 | 파일 유출 위험, 버전 관리 어려움 |
| **GitHub Secrets** | CI/CD 파이프라인, 스테이징 | GitHub 통합, 무료 | GitHub 플랫폼 의존, 로테이션 없음 |
| **AWS Secrets Manager** | 프로덕션 | 자동 로테이션, 감사 로그, IAM 통합 | 비용 발생 (비밀값당 월 $0.40) |
| **HashiCorp Vault** | 대규모 기업 | 멀티 클라우드, 고급 기능 | 운영 복잡도 높음 |

### 환경별 설정 파일 구조

```
myapp/
├── .env                         # 로컬 개발용 (git 제외 — .gitignore)
├── .env.example                 # 템플릿 (git 포함 — 실제 값 없음)
├── config/
│   ├── base.py                  # 모든 환경 공통 설정
│   ├── development.py           # 개발 환경 오버라이드
│   ├── staging.py               # 스테이징 환경 오버라이드
│   └── production.py            # 프로덕션 환경 오버라이드
├── docker-compose.yml           # 로컬 개발용 Docker Compose
├── docker-compose.test.yml      # 통합 테스트용
└── .gitignore
```

**.gitignore 필수 항목:**

```gitignore
# 환경변수 파일 (절대 커밋 금지)
.env
.env.local
.env.*.local
*.env

# 비밀 키 파일
*.pem
*.key
*.p12
secrets.json

# 테스트 커버리지
.coverage
htmlcov/
.pytest_cache/

# 빌드 산출물
__pycache__/
*.pyc
dist/
build/
node_modules/
```

### 12-Factor App 원칙 연결

**12-Factor App**은 Heroku가 정립한 클라우드 네이티브 애플리케이션 개발 방법론으로, 현대 CI/CD와 환경 관리의 이론적 토대입니다.

환경 관리와 직접 관련된 핵심 원칙:

| Factor | 원칙 이름 | 내용 | CI/CD 적용 |
|--------|---------|------|-----------|
| **III** | Config (설정) | 설정은 환경변수에 저장 | `.env`, GitHub Secrets 사용 |
| **IV** | Backing Services (백엔드 서비스) | DB, 캐시 등을 교체 가능한 리소스로 | 환경별 DATABASE_URL 분리 |
| **V** | Build, Release, Run | 빌드·릴리스·실행 단계 분리 | CI(빌드) → CD(릴리스+실행) |
| **X** | Dev/Prod Parity (개발/프로덕션 일치) | 개발과 프로덕션 환경을 최대한 유사하게 | 스테이징 환경으로 검증 |
| **XI** | Logs (로그) | 로그를 이벤트 스트림으로 처리 | CloudWatch, ELK Stack 연동 |

---

## 7. 핵심 정리

### CI/CD 도입 체크리스트

팀 프로젝트에서 CI/CD를 성공적으로 도입하기 위한 단계별 체크리스트입니다.

**1주차: 기반 구축**

```
□ GitHub Actions 워크플로우 파일 생성 (.github/workflows/ci.yml)
□ pytest 기본 테스트 작성 (최소 5개 이상)
□ Ruff 설정 파일 작성 (pyproject.toml)
□ .pre-commit-config.yaml 작성 및 설치
□ .env.example 파일 작성
□ .gitignore 점검 (.env 등 민감 파일 제외 확인)
□ GitHub Secrets에 API 키 등록
```

**2주차: 파이프라인 강화**

```
□ CI 파이프라인에 커버리지 측정 추가 (목표 60% → 80%)
□ 스테이징 환경 자동 배포 파이프라인 구성
□ Docker 이미지 빌드 및 ECR 푸시 자동화
□ Slack 또는 GitHub PR 코멘트 알림 연동
□ 브랜치 보호 규칙 설정 (CI 통과 필수)
```

**3주차: 품질 고도화**

```
□ 통합 테스트 작성 (DB 연동 테스트 포함)
□ E2E 테스트 1~2개 작성 (핵심 사용자 시나리오)
□ 프로덕션 배포 파이프라인 구성 (수동 승인 게이트 포함)
□ 롤백 절차 문서화 및 실습
□ 보안 스캔 추가 (bandit, safety)
```

### 품질 도구 선택 가이드

```
Python 프로젝트 시작 시 필수 도구 (최소 세트)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  린트 + 포매팅:  Ruff (속도·기능 모두 최고)
  타입 검사:      MyPy (타입 힌트 작성 습관화)
  테스트:         pytest + pytest-cov
  pre-commit:     pre-commit (커밋 전 자동 검사)

JavaScript/TypeScript 프로젝트 시 추가
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  린트:           ESLint
  포매팅:         Prettier
  Prettier + ESLint 충돌 방지: eslint-config-prettier

팀 규모가 커질 때 추가 검토
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  코드 품질 대시보드:  SonarCloud (GitHub 통합)
  의존성 보안 검사:    GitHub Dependabot
  비밀번호 유출 탐지:  GitLeaks, git-secrets
```

### CI/CD 핵심 개념 요약

| 개념 | 핵심 내용 |
|------|---------|
| **CI (지속적 통합)** | 코드 푸시 시 자동 빌드·테스트, 빠른 피드백, 통합 문제 조기 발견 |
| **CD (지속적 전달)** | 언제든지 배포 가능한 상태 유지, 수동 승인 후 배포 |
| **CD (지속적 배포)** | 테스트 통과 시 자동으로 프로덕션 배포 |
| **테스트 피라미드** | 단위(70%) > 통합(20%) > E2E(10%) 비율 유지 |
| **환경 분리** | Dev → Staging → Production 순서로 검증 후 배포 |
| **Secrets 관리** | 민감 정보는 코드에서 분리, GitHub Secrets / AWS Secrets Manager 활용 |
| **빠른 피드백** | CI 파이프라인은 10분 이내 완료 목표 |
| **롤백 전략** | 배포 전 롤백 방법과 기준을 사전에 정의 |

### 다음 단계

CI/CD의 기본 개념을 이해했다면, 이제 실제로 GitHub Actions를 사용하여 파이프라인을 구축하는 방법을 학습합니다.

**[→ 06_github_actions.md: GitHub Actions 실전](./06_github_actions.md)**

다음 강의에서 다루는 내용:
- GitHub Actions 워크플로우 문법 (YAML 구조, jobs, steps, on 트리거)
- 실제 CI 파이프라인 작성 (pytest + Ruff + Docker 빌드)
- 실제 CD 파이프라인 작성 (AWS ECS 자동 배포)
- 환경별 배포 파이프라인 구성 (Dev / Staging / Production)
- 재사용 가능한 워크플로우 (Reusable Workflows)
- GitHub Actions 보안 모범 사례

---
