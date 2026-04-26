# GitHub Actions 실전

> 코드를 작성하고 병합하는 순간, 자동으로 테스트가 실행되고, 품질이 검증되고, 컨테이너가 빌드되어 프로덕션에 배포되는 세상 — GitHub Actions는 이 모든 자동화를 YAML 파일 하나로 가능하게 합니다. 45일 과정의 마지막 기술 모듈에서 팀 프로젝트의 CI/CD 파이프라인을 완성합니다.

---

## 1. GitHub Actions 개요

### GitHub Actions란 무엇인가

GitHub Actions는 GitHub에 내장된 CI/CD(Continuous Integration / Continuous Delivery) 플랫폼입니다. 코드 저장소에서 발생하는 이벤트(push, pull request, 스케줄 등)를 트리거로 하여 자동화된 워크플로를 실행합니다. 별도의 외부 CI 서버(Jenkins, CircleCI 등)를 구축할 필요 없이, `.github/workflows/` 디렉토리에 YAML 파일을 추가하는 것만으로 파이프라인이 완성됩니다.

GitHub Actions가 팀 프로젝트에 필수인 이유는 다음과 같습니다. 첫째, 모든 PR이 병합되기 전에 자동으로 테스트를 통과해야 하므로 코드 품질이 보장됩니다. 둘째, 개발자가 수동으로 배포 스크립트를 실행하는 실수를 제거합니다. 셋째, 팀 전체가 동일한 빌드·테스트·배포 프로세스를 공유하여 "제 환경에서는 됩니다"라는 문제가 사라집니다.

### 핵심 개념 계층 구조

GitHub Actions의 구성 요소는 계층적으로 구성됩니다.

```mermaid
graph TD
    W["Workflow (워크플로)\n.github/workflows/*.yml"]
    E["Event (이벤트)\npush / pull_request\nschedule / workflow_dispatch"]
    J1["Job A\n(runs-on: ubuntu-latest)"]
    J2["Job B\n(runs-on: ubuntu-latest)"]
    S1["Step 1\ncheckout"]
    S2["Step 2\nsetup-python"]
    S3["Step 3\nrun tests"]
    S4["Step 4\nupload results"]
    A1["Action\nactions/checkout@v4"]
    A2["Action\nactions/setup-python@v5"]
    R["Runner\nGitHub-hosted\nor self-hosted"]

    W -->|triggered by| E
    W --> J1
    W --> J2
    J1 --> S1
    J1 --> S2
    J1 --> S3
    J1 --> S4
    S1 -->|uses| A1
    S2 -->|uses| A2
    J1 -->|runs on| R

    style W fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style E fill:#0984e3,stroke:#74b9ff,color:#fff
    style J1 fill:#00b894,stroke:#55efc4,color:#fff
    style J2 fill:#00b894,stroke:#55efc4,color:#fff
    style S1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style S2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style S3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style S4 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style A1 fill:#e17055,stroke:#fab1a0,color:#fff
    style A2 fill:#e17055,stroke:#fab1a0,color:#fff
    style R fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 핵심 용어 설명

**워크플로(Workflow)**는 `.github/workflows/` 디렉토리에 위치하는 YAML 파일입니다. 하나의 저장소에 여러 워크플로를 가질 수 있으며, 각각 독립적으로 트리거됩니다. 예를 들어 `ci.yml`은 PR마다 실행되고, `deploy.yml`은 main 브랜치에 병합될 때만 실행될 수 있습니다.

**이벤트(Event)**는 워크플로를 실행시키는 트리거입니다. GitHub에서 발생하는 거의 모든 활동이 이벤트가 될 수 있습니다. `push`, `pull_request`, `schedule`, `workflow_dispatch` 등이 가장 자주 사용됩니다.

**잡(Job)**은 워크플로 안의 실행 단위입니다. 기본적으로 잡들은 병렬로 실행됩니다. `needs` 키워드로 잡 간의 의존성을 설정하면 순차 실행이 가능합니다.

**스텝(Step)**은 잡 안에서 순차적으로 실행되는 개별 작업입니다. 쉘 명령어(`run:`)를 실행하거나, 미리 만들어진 액션(`uses:`)을 호출합니다.

**액션(Action)**은 재사용 가능한 단위 작업입니다. GitHub Marketplace에 수천 개의 공개 액션이 있으며, 직접 만들어 사용할 수도 있습니다.

**러너(Runner)**는 잡이 실행되는 서버 환경입니다. GitHub이 제공하는 호스팅 러너와 자체 서버에 설치하는 셀프호스팅 러너로 구분됩니다.

### 이벤트(Event) 종류

| 이벤트 | 트리거 조건 | 주요 사용 사례 |
|--------|-----------|--------------|
| `push` | 특정 브랜치에 커밋이 푸시될 때 | 병합 후 배포, 태그 릴리스 |
| `pull_request` | PR이 생성·수정·재오픈될 때 | CI 테스트, 린트 검사 |
| `pull_request_target` | 포크 저장소의 PR일 때 | 외부 기여자 PR 안전 처리 |
| `schedule` | cron 표현식으로 지정한 시간 | 야간 전체 테스트, 의존성 업데이트 |
| `workflow_dispatch` | GitHub UI 또는 API로 수동 실행 | 긴급 배포, 데이터 마이그레이션 |
| `workflow_call` | 다른 워크플로에서 호출 | 재사용 워크플로 |
| `release` | GitHub Release가 발행될 때 | 공식 릴리스 배포 |
| `repository_dispatch` | 외부 시스템에서 API 호출 | 웹훅 기반 트리거 |

### 러너(Runner) 비교

| 구분 | GitHub-hosted (ubuntu-latest) | GitHub-hosted (windows/macos) | Self-hosted |
|------|-------------------------------|-------------------------------|-------------|
| **비용** | Public 저장소 무료, Private 월 2,000분 무료 | ubuntu보다 소비 배율 높음 (windows 2x, macos 10x) | 서버 비용만 발생 |
| **환경** | 매 실행마다 초기화된 깨끗한 VM | 동일 | 영속적 환경 유지 가능 |
| **사전 설치** | Python, Node, Docker 등 다수 | OS별 상이 | 직접 설치 필요 |
| **성능** | 2코어 7GB RAM | 상이 | 자체 서버 성능에 따름 |
| **네트워크** | 외부 인터넷 허용 | 외부 인터넷 허용 | 내부망 접근 가능 |
| **주요 용도** | 대부분의 CI/CD | OS별 크로스 테스트 | 대용량 빌드, 보안 환경 |

> **핵심 포인트:** 팀 프로젝트에서는 `ubuntu-latest`를 기본으로 사용합니다. AWS 리소스에 접근할 때는 셀프호스팅 러너보다 OIDC 방식의 임시 자격증명을 활용하는 것이 더 안전합니다.

---

## 2. 워크플로 YAML 구조

### 기본 구조 분석

YAML 워크플로의 최상위 구조는 다음과 같습니다.

```yaml
name: 워크플로 이름              # GitHub UI에 표시되는 이름

on:                              # 이벤트 트리거 설정
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:                     # GITHUB_TOKEN 권한 (최소 권한 원칙)
  contents: read
  pull-requests: write

concurrency:                     # 동시 실행 제어
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:                            # 하나 이상의 잡 정의
  job-name:
    runs-on: ubuntu-latest
    steps:
      - name: 스텝 이름
        uses: actions/checkout@v4
```

### `on` 이벤트 설정

#### 브랜치 필터와 paths 필터

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'       # release/로 시작하는 모든 브랜치
      - '!hotfix/**'       # hotfix/로 시작하는 브랜치 제외
    paths:
      - 'src/**'           # src 디렉토리 하위 파일 변경 시에만 실행
      - 'requirements*.txt'
      - '!docs/**'         # docs 변경은 무시

  pull_request:
    branches: [main, develop]
    types:
      - opened            # PR 생성 시
      - synchronize       # 새 커밋 푸시 시
      - reopened          # 닫힌 PR 재오픈 시

  schedule:
    - cron: '0 2 * * 1-5'   # 평일 오전 2시 (UTC) 실행

  workflow_dispatch:
    inputs:
      environment:
        description: '배포 대상 환경'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      dry_run:
        description: '실제 배포 없이 계획만 출력'
        required: false
        type: boolean
        default: false
```

### `jobs` 설정

#### runs-on과 strategy matrix

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false          # 하나가 실패해도 나머지 계속 실행
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, windows-latest]
        exclude:
          - os: windows-latest
            python-version: '3.10'

    steps:
      - name: Python ${{ matrix.python-version }} on ${{ matrix.os }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

#### needs - 잡 의존성

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "린트 검사"

  test:
    runs-on: ubuntu-latest
    needs: lint               # lint 잡이 성공해야 test 시작
    steps:
      - run: echo "테스트 실행"

  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test]       # 두 잡 모두 성공해야 배포
    steps:
      - run: echo "배포 실행"
```

### `steps` 설정

#### uses, run, with, env

```yaml
steps:
  # 액션 사용 (Marketplace 또는 로컬)
  - name: 소스 코드 체크아웃
    uses: actions/checkout@v4
    with:
      fetch-depth: 0           # 전체 히스토리 가져오기 (태그 포함)
      token: ${{ secrets.GITHUB_TOKEN }}

  # 쉘 명령어 실행
  - name: 의존성 설치
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
    env:
      PIP_NO_CACHE_DIR: 1
      DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

  # 멀티라인 환경변수
  - name: 설정 파일 생성
    run: |
      cat > .env << EOF
      ENVIRONMENT=test
      API_KEY=${{ secrets.API_KEY }}
      EOF
```

### 조건부 실행 (if)

```yaml
steps:
  # 이벤트 종류에 따른 조건
  - name: main 브랜치에만 실행
    if: github.ref == 'refs/heads/main'
    run: echo "main 브랜치입니다"

  # 이전 스텝 결과에 따른 조건
  - name: 테스트 실패 시에만 슬랙 알림
    if: failure()
    uses: slackapi/slack-github-action@v1.26.0
    with:
      payload: '{"text": "테스트 실패!"}'

  # 여러 조건 조합
  - name: PR이 main을 대상으로 할 때만
    if: >
      github.event_name == 'pull_request' &&
      github.base_ref == 'main' &&
      success()
    run: echo "PR to main"

  # 항상 실행 (이전 스텝 실패 포함)
  - name: 정리 작업
    if: always()
    run: rm -rf /tmp/build-*
```

### concurrency와 permissions

```yaml
# 동일 브랜치의 이전 워크플로 실행을 취소
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# GITHUB_TOKEN 권한 최소화 (보안 모범 사례)
permissions:
  contents: read          # 코드 읽기
  pull-requests: write    # PR 댓글 작성
  checks: write           # 체크 결과 업데이트
  id-token: write         # OIDC 토큰 (AWS 인증에 필요)
```

> **핵심 포인트:** `permissions`를 명시하지 않으면 GITHUB_TOKEN에 과도한 권한이 부여됩니다. 최소 권한 원칙에 따라 필요한 권한만 명시하는 것이 보안 모범 사례입니다.

---

## 3. CI 워크플로

### CI(Continuous Integration)의 목적

CI 워크플로는 코드가 병합되기 전에 품질을 자동으로 검증합니다. 팀 프로젝트에서 CI 없이 PR을 병합하면, 품질이 낮은 코드가 누적되어 프로젝트 후반부에 기술 부채가 폭발합니다. CI는 다음을 자동화합니다.

- **린트(Lint)**: 코드 스타일, 잠재적 버그 패턴 검사 (ruff)
- **포맷 검사**: 코드 형식 일관성 확인 (black)
- **타입 검사**: 타입 힌트 정확성 확인 (mypy)
- **테스트**: 유닛·통합 테스트 실행 (pytest)
- **커버리지**: 테스트 커버리지 측정 및 리포트

### CI 워크플로 흐름

```mermaid
flowchart TB
    A["push / PR"]:::purple --> B["checkout + setup-python"]:::blue
    B --> C["cache + pip install"]:::blue
    C --> D["ruff lint"]:::yellow
    D --> E{"린트 통과?"}
    E -->|"실패"| Z1["워크플로 실패"]:::orange
    E -->|"성공"| F["black + mypy"]:::yellow
    F --> G["pytest + coverage"]:::yellow
    G --> H["codecov + PR 댓글"]:::green
    H --> I["PR 병합 가능"]:::green

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
```

### Python 프로젝트 전체 CI YAML

아래는 FastAPI AI 서비스에 바로 적용할 수 있는 완전한 CI 워크플로입니다. `.github/workflows/ci.yml`로 저장합니다.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'src/**'
      - 'tests/**'
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/ci.yml'
  pull_request:
    branches:
      - main
      - develop
    types:
      - opened
      - synchronize
      - reopened

# 동시 실행 제어: 같은 브랜치의 이전 워크플로 취소
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# 최소 권한 설정
permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  # ─────────────────────────────────────────────
  # 잡 1: 린트 및 포맷 검사
  # ─────────────────────────────────────────────
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest

    steps:
      - name: 소스 코드 체크아웃
        uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: pip 캐시 설정
        uses: actions/cache@v4
        id: pip-cache
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-lint-${{ hashFiles('requirements*.txt', 'pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-lint-
            ${{ runner.os }}-pip-

      - name: 린트 도구 설치
        run: |
          python -m pip install --upgrade pip
          pip install ruff black mypy

      - name: Ruff 린트 검사
        run: |
          ruff check src/ tests/ --output-format=github
        continue-on-error: false

      - name: Black 포맷 검사
        run: |
          black --check --diff src/ tests/

      - name: Mypy 타입 검사
        run: |
          pip install -r requirements.txt  # 타입 스텁을 위해 전체 의존성 필요
          mypy src/ --ignore-missing-imports --strict
        continue-on-error: true            # 타입 오류는 경고로 처리 (팀 상황에 따라 조정)

  # ─────────────────────────────────────────────
  # 잡 2: 테스트 실행 (matrix)
  # ─────────────────────────────────────────────
  test:
    name: Test (Python ${{ matrix.python-version }}, ${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    needs: lint                            # lint 통과 후 실행

    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest]
        include:
          - python-version: '3.11'
            os: ubuntu-latest
            upload-coverage: true         # 커버리지는 한 번만 업로드

    env:
      PYTHONPATH: src
      ENVIRONMENT: test
      DATABASE_URL: sqlite:///./test.db   # 테스트용 SQLite

    steps:
      - name: 소스 코드 체크아웃
        uses: actions/checkout@v4
        with:
          fetch-depth: 0                  # 커버리지 비교를 위해 전체 히스토리

      - name: Python ${{ matrix.python-version }} 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'                    # actions/setup-python 내장 캐시

      - name: pip 캐시 설정 (세밀한 제어)
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-py${{ matrix.python-version }}-
            ${{ runner.os }}-pip-

      - name: 의존성 설치
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: pytest 실행 (커버리지 포함)
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml:coverage.xml \
            --cov-report=html:htmlcov \
            --cov-report=term-missing \
            --cov-fail-under=70 \
            -v \
            --tb=short \
            --junitxml=junit.xml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_TEST }}

      - name: 테스트 결과 업로드 (항상 실행)
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-py${{ matrix.python-version }}-${{ matrix.os }}
          path: |
            junit.xml
            coverage.xml
            htmlcov/
          retention-days: 7

      - name: JUnit 테스트 리포트 PR 댓글
        uses: dorny/test-reporter@v1
        if: always() && matrix.upload-coverage
        with:
          name: Pytest Results (Python ${{ matrix.python-version }})
          path: junit.xml
          reporter: java-junit
          fail-on-error: true

      - name: 커버리지 리포트 업로드 (Codecov)
        uses: codecov/codecov-action@v4
        if: matrix.upload-coverage
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
          name: codecov-py${{ matrix.python-version }}
          fail_ci_if_error: false

      - name: PR 커버리지 댓글
        uses: py-cov-action/python-coverage-comment-action@v3
        if: matrix.upload-coverage && github.event_name == 'pull_request'
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          COVERAGE_PATH: coverage.xml

  # ─────────────────────────────────────────────
  # 잡 3: CI 통과 확인 (브랜치 보호 규칙용 단일 체크)
  # ─────────────────────────────────────────────
  ci-success:
    name: CI Success
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: always()

    steps:
      - name: 모든 잡 성공 확인
        run: |
          if [[ "${{ needs.lint.result }}" == "success" && \
                "${{ needs.test.result }}" == "success" ]]; then
            echo "모든 CI 검사가 통과되었습니다."
            exit 0
          else
            echo "CI 검사 실패: lint=${{ needs.lint.result }}, test=${{ needs.test.result }}"
            exit 1
          fi
```

### pip 캐시 전략 설명

캐시를 올바르게 설정하면 의존성 설치 시간을 대폭 줄일 수 있습니다.

| 캐시 전략 | 캐시 키 구성 | 적합한 상황 |
|-----------|------------|-----------|
| **정확 매칭** | `os-py버전-requirements해시` | 의존성이 자주 바뀌지 않을 때 |
| **복원 키 계층** | 정확 → OS+버전 → OS만 | 항상 권장 (캐시 히트율 최대화) |
| **setup-python 내장** | `cache: 'pip'` 한 줄로 자동 | 단순한 경우 |

> **핵심 포인트:** `hashFiles('requirements*.txt')` 패턴을 사용하면 `requirements.txt`와 `requirements-dev.txt` 모두 변경을 감지합니다. `pyproject.toml`도 추가하면 Poetry나 Hatch 프로젝트에서도 올바르게 동작합니다.

---

## 4. Docker 빌드 워크플로

### Docker 빌드 및 ECR 푸시 흐름

```mermaid
flowchart TD
    A["main push"]:::purple --> B["OIDC + ECR 로그인"]:::blue
    B --> C["Buildx + 캐시 설정"]:::blue
    C --> D["이미지 빌드 + 태그"]:::yellow
    D --> E{"빌드 성공?"}
    E -->|"실패"| Z["Slack 실패 알림"]:::orange
    E -->|"성공"| F["ECR 푸시"]:::green
    F --> G["ECS 태스크 업데이트"]:::green
    G --> H["ECS 배포 + 대기"]:::green
    H --> I{"배포 성공?"}
    I -->|"성공"| J["Slack 성공 알림"]:::green
    I -->|"실패"| K["롤백 + 실패 알림"]:::orange

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
```

### Docker 빌드 및 배포 전체 YAML

`.github/workflows/docker-build.yml`로 저장합니다.

```yaml
# .github/workflows/docker-build.yml
name: Docker Build & Deploy

on:
  push:
    branches:
      - main
    paths:
      - 'src/**'
      - 'Dockerfile'
      - 'docker-compose*.yml'
      - 'requirements*.txt'
      - '.github/workflows/docker-build.yml'
  workflow_dispatch:
    inputs:
      force_deploy:
        description: '강제 배포 (코드 변경 없어도 실행)'
        type: boolean
        default: false

concurrency:
  group: docker-deploy-${{ github.ref }}
  cancel-in-progress: false              # 배포는 취소하지 않음

permissions:
  id-token: write                        # OIDC 필수
  contents: read
  packages: write

env:
  AWS_REGION: ap-northeast-2
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-northeast-2.amazonaws.com
  ECR_REPOSITORY: my-ai-service
  ECS_CLUSTER: my-ai-cluster
  ECS_SERVICE: my-ai-service
  CONTAINER_NAME: app

jobs:
  build-and-push:
    name: Build & Push to ECR
    runs-on: ubuntu-latest

    outputs:
      image-uri: ${{ steps.image-meta.outputs.image-uri }}
      image-tag: ${{ steps.image-meta.outputs.image-tag }}

    steps:
      - name: 소스 코드 체크아웃
        uses: actions/checkout@v4

      # ── AWS OIDC 인증 (비밀키 없이 임시 자격증명) ──
      - name: AWS 자격증명 설정 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          role-session-name: GitHubActions-${{ github.run_id }}
          aws-region: ${{ env.AWS_REGION }}

      # ── ECR 로그인 ──
      - name: Amazon ECR 로그인
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      # ── 이미지 태그 생성 ──
      - name: 이미지 메타데이터 생성
        id: image-meta
        run: |
          SHORT_SHA=$(echo "${{ github.sha }}" | cut -c1-7)
          DATE=$(date +%Y%m%d)
          IMAGE_TAG="${DATE}-${SHORT_SHA}"
          IMAGE_URI="${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${IMAGE_TAG}"
          echo "image-tag=${IMAGE_TAG}" >> "$GITHUB_OUTPUT"
          echo "image-uri=${IMAGE_URI}" >> "$GITHUB_OUTPUT"
          echo "short-sha=${SHORT_SHA}" >> "$GITHUB_OUTPUT"
          echo "빌드 이미지: ${IMAGE_URI}"

      # ── Docker Buildx 설정 (멀티플랫폼, 캐시 지원) ──
      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3
        with:
          install: true

      # ── GitHub Actions 캐시로 Docker 레이어 캐싱 ──
      - name: Docker 레이어 캐시
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ hashFiles('Dockerfile', 'requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-buildx-

      # ── 이미지 빌드 및 ECR 푸시 ──
      - name: Docker 이미지 빌드 및 푸시
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          platforms: linux/amd64
          push: true
          tags: |
            ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ steps.image-meta.outputs.image-tag }}
            ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:latest
          build-args: |
            BUILD_DATE=${{ github.run_id }}
            GIT_SHA=${{ github.sha }}
            GIT_REF=${{ github.ref_name }}
          cache-from: type=local,src=/tmp/.buildx-cache
          cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
          labels: |
            org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
            org.opencontainers.image.revision=${{ github.sha }}
            org.opencontainers.image.created=${{ github.event.head_commit.timestamp }}

      # ── 캐시 순환 (캐시 크기 무제한 증가 방지) ──
      - name: 빌드 캐시 이동
        run: |
          rm -rf /tmp/.buildx-cache
          mv /tmp/.buildx-cache-new /tmp/.buildx-cache

      - name: 빌드 완료 요약
        run: |
          echo "## Docker 빌드 완료" >> "$GITHUB_STEP_SUMMARY"
          echo "- **이미지**: \`${{ steps.image-meta.outputs.image-uri }}\`" >> "$GITHUB_STEP_SUMMARY"
          echo "- **태그**: \`${{ steps.image-meta.outputs.image-tag }}\`" >> "$GITHUB_STEP_SUMMARY"
          echo "- **SHA**: \`${{ github.sha }}\`" >> "$GITHUB_STEP_SUMMARY"

  deploy-to-ecs:
    name: Deploy to ECS
    runs-on: ubuntu-latest
    needs: build-and-push

    steps:
      - name: AWS 자격증명 설정 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          role-session-name: GitHubActions-Deploy-${{ github.run_id }}
          aws-region: ${{ env.AWS_REGION }}

      - name: 현재 ECS 태스크 정의 다운로드
        id: download-task-def
        run: |
          aws ecs describe-task-definition \
            --task-definition ${{ env.ECS_SERVICE }} \
            --query taskDefinition \
            > task-definition.json
          echo "태스크 정의 다운로드 완료"
          cat task-definition.json | jq '.containerDefinitions[0].image'

      - name: 태스크 정의에 새 이미지 URI 업데이트
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ needs.build-and-push.outputs.image-uri }}
          environment-variables: |
            GIT_SHA=${{ github.sha }}
            DEPLOYED_AT=${{ github.event.head_commit.timestamp }}

      - name: ECS 서비스에 새 태스크 정의 배포
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true   # 배포 완료까지 대기
          wait-for-minutes: 10               # 최대 10분 대기

      - name: 배포 완료 요약
        if: success()
        run: |
          echo "## ECS 배포 완료" >> "$GITHUB_STEP_SUMMARY"
          echo "- **클러스터**: \`${{ env.ECS_CLUSTER }}\`" >> "$GITHUB_STEP_SUMMARY"
          echo "- **서비스**: \`${{ env.ECS_SERVICE }}\`" >> "$GITHUB_STEP_SUMMARY"
          echo "- **이미지**: \`${{ needs.build-and-push.outputs.image-uri }}\`" >> "$GITHUB_STEP_SUMMARY"

      - name: Slack 배포 성공 알림
        if: success()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "✅ 프로덕션 배포 성공",
              "attachments": [
                {
                  "color": "#00b894",
                  "fields": [
                    {"title": "서비스", "value": "${{ env.ECS_SERVICE }}", "short": true},
                    {"title": "이미지", "value": "${{ needs.build-and-push.outputs.image-tag }}", "short": true},
                    {"title": "커밋", "value": "${{ github.event.head_commit.message }}", "short": false},
                    {"title": "배포자", "value": "${{ github.actor }}", "short": true},
                    {"title": "링크", "value": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}", "short": false}
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

      - name: Slack 배포 실패 알림
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "❌ 프로덕션 배포 실패",
              "attachments": [
                {
                  "color": "#e17055",
                  "fields": [
                    {"title": "서비스", "value": "${{ env.ECS_SERVICE }}", "short": true},
                    {"title": "이미지", "value": "${{ needs.build-and-push.outputs.image-tag }}", "short": true},
                    {"title": "오류", "value": "워크플로 로그를 확인하세요", "short": false},
                    {"title": "링크", "value": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}", "short": false}
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

### 이미지 태깅 전략

| 태그 패턴 | 예시 | 장점 | 단점 |
|-----------|------|------|------|
| `latest` | `myapp:latest` | 간단 | 어떤 버전인지 알 수 없음 |
| Git SHA | `myapp:a1b2c3d` | 정확한 버전 추적 | 사람이 읽기 어려움 |
| 날짜+SHA | `myapp:20240115-a1b2c3d` | 날짜와 버전 모두 파악 | 권장 방식 |
| 시맨틱 버전 | `myapp:v1.2.3` | 명확한 버전 관리 | 태그 관리 필요 |
| 브랜치명 | `myapp:main` | 환경 추적 가능 | 덮어쓰기 발생 |

> **핵심 포인트:** 프로덕션 이미지에는 `latest` 태그만 사용하지 마세요. `latest`와 함께 고유한 태그(날짜+SHA)를 항상 같이 붙이면, 문제 발생 시 특정 버전으로 롤백하는 것이 쉬워집니다.

---

## 5. AWS 배포 워크플로

### OIDC 인증 — 비밀 키 없이 AWS 인증

기존 방식은 AWS Access Key와 Secret Key를 GitHub Secrets에 저장했습니다. 이 방법은 키가 유출될 경우 보안 사고로 이어집니다. OIDC(OpenID Connect)를 사용하면 GitHub Actions가 임시 자격증명을 요청하므로 장기 키를 저장할 필요가 없습니다.

#### OIDC 동작 원리

1. GitHub Actions 러너가 GitHub의 OIDC 엔드포인트에서 JWT 토큰을 발급받습니다.
2. AWS STS(Security Token Service)에 이 JWT를 제시하며 역할 임시 위임을 요청합니다.
3. AWS는 GitHub의 공개 키로 JWT를 검증하고, IAM 역할 신뢰 정책과 조건을 확인합니다.
4. 검증 성공 시 만료 시간이 있는 임시 자격증명(Access Key, Secret Key, Session Token)을 반환합니다.

#### IAM Role 신뢰 정책 (Trust Policy)

AWS IAM 콘솔에서 새 역할을 만들 때 사용하는 신뢰 정책 JSON입니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsOIDC",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:your-org/your-repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

조건을 더 유연하게 설정하려면 `StringLike`를 사용합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsOIDCFlexible",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:your-org/your-repo:*"
        }
      }
    }
  ]
}
```

#### OIDC 설정 단계

AWS에서 GitHub OIDC Provider를 설정하는 단계입니다.

```bash
# 1. AWS CLI로 OIDC Provider 생성 (한 번만 실행)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. IAM 역할 생성 (trust-policy.json 파일 사용)
aws iam create-role \
  --role-name GitHubActionsRole \
  --assume-role-policy-document file://trust-policy.json

# 3. 필요한 권한 정책 연결
aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

# 4. 역할 ARN 확인
aws iam get-role --role-name GitHubActionsRole \
  --query 'Role.Arn' --output text
```

### 최소 권한 IAM 정책

GitHub Actions에 부여할 IAM 정책을 최소화합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAuth",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRPushPull",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:ap-northeast-2:123456789012:repository/my-ai-service"
    },
    {
      "Sid": "ECSDeployment",
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTasks",
        "ecs:ListTasks",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": [
        "arn:aws:ecs:ap-northeast-2:123456789012:cluster/my-ai-cluster",
        "arn:aws:ecs:ap-northeast-2:123456789012:service/my-ai-cluster/my-ai-service",
        "arn:aws:ecs:ap-northeast-2:123456789012:task-definition/my-ai-service:*"
      ]
    },
    {
      "Sid": "PassRoleToECS",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "ecs-tasks.amazonaws.com"
        }
      }
    }
  ]
}
```

### ECS 배포 및 안정성 대기

`aws-actions/amazon-ecs-deploy-task-definition`의 `wait-for-service-stability: true` 옵션은 ECS 서비스가 새 태스크 정의로 완전히 전환될 때까지 워크플로를 블로킹합니다.

```yaml
- name: ECS 배포 및 안정성 대기
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.task-def.outputs.task-definition }}
    service: my-ai-service
    cluster: my-ai-cluster
    wait-for-service-stability: true
    wait-for-minutes: 15               # 기본값 30분, 필요에 따라 조정
    codedeploy-appspec: |              # CodeDeploy 블루/그린 배포 시
      version: 0.0
      Resources:
        - TargetService:
            Type: AWS::ECS::Service
            Properties:
              TaskDefinition: <TASK_DEFINITION>
              LoadBalancerInfo:
                ContainerName: app
                ContainerPort: 8000
```

> **핵심 포인트:** `wait-for-service-stability: true`를 사용하면 배포가 실패했을 때 GitHub Actions 워크플로도 실패로 표시됩니다. 이를 통해 실패한 배포를 즉시 인지하고 Slack 알림을 통해 팀에 전파할 수 있습니다.

---

## 6. 고급 기능

### 재사용 워크플로 (Reusable Workflows)

여러 저장소나 워크플로에서 공통으로 사용하는 로직을 `workflow_call`로 분리합니다.

#### 재사용 워크플로 정의 (`/.github/workflows/reusable-deploy.yml`)

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
        description: '배포 대상 환경 (staging/production)'
      image-tag:
        required: true
        type: string
        description: '배포할 Docker 이미지 태그'
      ecs-service:
        required: true
        type: string
    secrets:
      AWS_GITHUB_ACTIONS_ROLE_ARN:
        required: true
      SLACK_WEBHOOK_URL:
        required: true
    outputs:
      deployed-task-arn:
        description: '배포된 ECS 태스크 ARN'
        value: ${{ jobs.deploy.outputs.task-arn }}

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}   # GitHub Environment 연결

    outputs:
      task-arn: ${{ steps.deploy.outputs.task-definition-arn }}

    steps:
      - name: AWS 자격증명 설정
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          aws-region: ap-northeast-2

      - name: ECS 배포
        id: deploy
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ inputs.ecs-service }}
          service: ${{ inputs.ecs-service }}
          cluster: my-ai-cluster-${{ inputs.environment }}
          wait-for-service-stability: true

      - name: Slack 알림
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "${{ job.status == 'success' && '✅' || '❌' }} ${{ inputs.environment }} 배포 ${{ job.status }}",
              "attachments": [{
                "color": "${{ job.status == 'success' && '#00b894' || '#e17055' }}",
                "fields": [
                  {"title": "환경", "value": "${{ inputs.environment }}", "short": true},
                  {"title": "이미지 태그", "value": "${{ inputs.image-tag }}", "short": true}
                ]
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

#### 재사용 워크플로 호출

```yaml
# .github/workflows/deploy-pipeline.yml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
      image-tag: ${{ needs.build.outputs.image-tag }}
      ecs-service: my-ai-service-staging
    secrets:
      AWS_GITHUB_ACTIONS_ROLE_ARN: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Composite Actions

단일 잡 안에서 재사용 가능한 스텝 묶음입니다. 마켓플레이스에 배포할 수도 있고, 저장소 내부에서만 사용할 수도 있습니다.

#### Composite Action 정의 (`.github/actions/setup-python-poetry/action.yml`)

```yaml
# .github/actions/setup-python-poetry/action.yml
name: Setup Python with Poetry
description: Python과 Poetry를 설정하고 의존성을 캐시와 함께 설치합니다

inputs:
  python-version:
    description: 'Python 버전'
    required: false
    default: '3.11'
  working-directory:
    description: '작업 디렉토리'
    required: false
    default: '.'

outputs:
  cache-hit:
    description: 'pip 캐시 히트 여부'
    value: ${{ steps.pip-cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - name: Python 설정
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}

    - name: pip 캐시
      id: pip-cache
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-py${{ inputs.python-version }}-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}
        restore-keys: |
          ${{ runner.os }}-py${{ inputs.python-version }}-

    - name: 의존성 설치
      shell: bash
      working-directory: ${{ inputs.working-directory }}
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then
          pip install -r requirements.txt
        fi
        if [ -f requirements-dev.txt ]; then
          pip install -r requirements-dev.txt
        fi
```

#### Composite Action 사용

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Python 환경 설정
    uses: ./.github/actions/setup-python-poetry
    with:
      python-version: '3.11'

  - name: 테스트 실행
    run: pytest tests/
```

### GitHub Environments

`staging`과 `production` 환경을 구분하고 승인 게이트를 설정합니다.

| 기능 | 설명 | 설정 위치 |
|------|------|-----------|
| **Required Reviewers** | 배포 전 지정한 팀원의 승인 필요 | Environments → Required reviewers |
| **Wait Timer** | 배포 전 대기 시간 설정 | Environments → Wait timer |
| **Deployment Branches** | 특정 브랜치만 해당 환경에 배포 허용 | Environments → Deployment branches |
| **Environment Secrets** | 환경별 별도 시크릿 | Environments → Secrets |
| **Environment Variables** | 환경별 변수 | Environments → Variables |

```yaml
jobs:
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment:
      name: production                   # GitHub Environment 이름
      url: https://api.myservice.com     # 배포 후 표시될 URL
    needs: [deploy-staging, approval]
```

### Repository Secrets vs Environment Secrets

| 구분 | Repository Secrets | Environment Secrets |
|------|--------------------|---------------------|
| **범위** | 저장소 전체 모든 잡 | 특정 Environment를 사용하는 잡만 |
| **접근 제어** | 저장소 관리자 | Environment 보호 규칙에 따름 |
| **주요 용도** | API 키, 공통 토큰 | 환경별 AWS 자격증명, DB 비밀번호 |
| **예시** | `SLACK_WEBHOOK_URL` | `DATABASE_URL`, `JWT_SECRET` |
| **보안 수준** | 기본 | 더 높음 (승인 필요 설정 가능) |

### GitHub Actions 비용 관리

| 항목 | Public 저장소 | Private 저장소 |
|------|--------------|--------------|
| **ubuntu-latest 분당 비용** | 무료 | $0.008 |
| **windows-latest 분당 비용** | 무료 | $0.016 (2x) |
| **macos-latest 분당 비용** | 무료 | $0.08 (10x) |
| **월 무료 분** | 무한 | 2,000분 |
| **스토리지 무료** | 무한 | 500MB |
| **스토리지 초과 요금** | 무료 | GB당 $0.25/월 |

**비용 절감 방법:**

- `paths:` 필터로 불필요한 워크플로 실행 방지
- `concurrency`로 중복 실행 취소 (`cancel-in-progress: true`)
- 캐시 활용으로 의존성 설치 시간 단축
- 매트릭스 테스트는 필수 조합만 유지
- `timeout-minutes:` 설정으로 무한 실행 방지
- Artifact 보존 기간 단축 (`retention-days: 7`)

> **핵심 포인트:** 팀 저장소를 Private으로 유지하면서 월 2,000분을 초과하지 않으려면, CI 워크플로의 `paths:` 필터를 잘 설정하는 것이 가장 효과적입니다. `docs/`나 `*.md` 파일 변경만으로는 CI가 실행되지 않도록 제한하면 무의미한 실행을 크게 줄일 수 있습니다.

---

## 7. 실전 파이프라인

### FastAPI AI 서비스 전체 CI/CD 파이프라인

실제 팀 프로젝트에서 사용하는 완전한 파이프라인의 전체 흐름을 먼저 이해합니다.

```mermaid
flowchart TB
    A["feature Push"]:::purple --> B["CI: Lint + Test"]:::blue
    B --> C{"CI 통과?"}
    C -->|"실패"| Z1["PR 차단"]:::orange
    C -->|"성공"| D["PR 리뷰 + 승인"]:::yellow
    D --> E["main 병합"]:::green
    E --> F["Docker 빌드 + ECR 푸시"]:::green
    F --> G["Staging 배포 + 테스트"]:::green
    G --> H{"Staging 정상?"}
    H -->|"실패"| Z2["Staging 롤백"]:::orange
    H -->|"성공"| I["PM 승인 후 Prod 배포"]:::yellow
    I --> J{"Prod 정상?"}
    J -->|"실패"| Z3["Prod 롤백"]:::orange
    J -->|"성공"| K["배포 완료"]:::green

    classDef purple fill:#6c5ce7,stroke:#a29bfe,color:#fff
    classDef blue fill:#0984e3,stroke:#74b9ff,color:#fff
    classDef yellow fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    classDef green fill:#00b894,stroke:#55efc4,color:#fff
    classDef orange fill:#e17055,stroke:#fab1a0,color:#fff
```

### 통합 CI/CD 파이프라인 전체 YAML

`.github/workflows/pipeline.yml`로 저장합니다. 이 파일 하나에 CI, Docker 빌드, Staging 배포, Production 배포가 모두 포함됩니다.

```yaml
# .github/workflows/pipeline.yml
name: Full CI/CD Pipeline

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      environment:
        description: '강제 배포 환경'
        type: choice
        options: [staging, production]
        required: true

concurrency:
  group: pipeline-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

permissions:
  id-token: write
  contents: read
  pull-requests: write
  checks: write

env:
  AWS_REGION: ap-northeast-2
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-northeast-2.amazonaws.com
  ECR_REPOSITORY: my-ai-service
  PYTHON_VERSION: '3.11'

jobs:
  # ══════════════════════════════════════════════════════
  # 1단계: 린트 및 품질 검사
  # ══════════════════════════════════════════════════════
  quality:
    name: Code Quality
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: 개발 의존성 설치
        run: |
          pip install --upgrade pip
          pip install ruff black mypy
          pip install -r requirements.txt

      - name: Ruff 린트
        run: ruff check src/ tests/ --output-format=github

      - name: Black 포맷 검사
        run: black --check src/ tests/

      - name: Mypy 타입 검사
        run: mypy src/ --ignore-missing-imports
        continue-on-error: true

  # ══════════════════════════════════════════════════════
  # 2단계: 테스트 및 커버리지
  # ══════════════════════════════════════════════════════
  test:
    name: Test & Coverage
    runs-on: ubuntu-latest
    needs: quality

    services:
      # 통합 테스트를 위한 PostgreSQL
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      # Redis 캐시 테스트
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
      REDIS_URL: redis://localhost:6379
      ENVIRONMENT: test
      PYTHONPATH: src

    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: 의존성 설치
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: 데이터베이스 마이그레이션
        run: |
          alembic upgrade head
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb

      - name: pytest 실행
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=70 \
            -v \
            --junitxml=junit.xml \
            -x
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}

      - name: 테스트 결과 아티팩트 업로드
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            junit.xml
            coverage.xml
          retention-days: 7

      - name: Codecov 업로드
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage.xml

      - name: PR 커버리지 댓글
        uses: py-cov-action/python-coverage-comment-action@v3
        if: github.event_name == 'pull_request'
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          COVERAGE_PATH: coverage.xml

  # ══════════════════════════════════════════════════════
  # 3단계: Docker 빌드 및 ECR 푸시 (main 브랜치 푸시 시에만)
  # ══════════════════════════════════════════════════════
  build:
    name: Docker Build & Push
    runs-on: ubuntu-latest
    needs: [quality, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    outputs:
      image-tag: ${{ steps.meta.outputs.image-tag }}
      image-uri: ${{ steps.meta.outputs.image-uri }}

    steps:
      - uses: actions/checkout@v4

      - name: AWS 자격증명 설정 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          role-session-name: GitHubActions-Build-${{ github.run_id }}
          aws-region: ${{ env.AWS_REGION }}

      - name: ECR 로그인
        uses: aws-actions/amazon-ecr-login@v2

      - name: 이미지 메타데이터
        id: meta
        run: |
          SHORT_SHA=$(echo "${{ github.sha }}" | cut -c1-7)
          DATE=$(date +%Y%m%d)
          TAG="${DATE}-${SHORT_SHA}"
          URI="${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${TAG}"
          echo "image-tag=${TAG}" >> "$GITHUB_OUTPUT"
          echo "image-uri=${URI}" >> "$GITHUB_OUTPUT"

      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3

      - name: Docker 레이어 캐시
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ hashFiles('Dockerfile', 'requirements*.txt') }}
          restore-keys: ${{ runner.os }}-buildx-

      - name: 이미지 빌드 및 ECR 푸시
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ steps.meta.outputs.image-tag }}
            ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:latest
          cache-from: type=local,src=/tmp/.buildx-cache
          cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max

      - name: 캐시 이동
        run: |
          rm -rf /tmp/.buildx-cache
          mv /tmp/.buildx-cache-new /tmp/.buildx-cache

  # ══════════════════════════════════════════════════════
  # 4단계: Staging 배포 (자동)
  # ══════════════════════════════════════════════════════
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: staging
      url: https://staging-api.myservice.com

    steps:
      - uses: actions/checkout@v4

      - name: AWS 자격증명 설정
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          role-session-name: GitHubActions-Staging-${{ github.run_id }}
          aws-region: ${{ env.AWS_REGION }}

      - name: 태스크 정의 다운로드
        run: |
          aws ecs describe-task-definition \
            --task-definition my-ai-service-staging \
            --query taskDefinition \
            > task-definition.json

      - name: 이미지 URI 업데이트
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: app
          image: ${{ needs.build.outputs.image-uri }}

      - name: Staging 배포
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: my-ai-service-staging
          cluster: my-ai-cluster-staging
          wait-for-service-stability: true
          wait-for-minutes: 10

      - name: Staging 스모크 테스트
        run: |
          sleep 30
          HEALTH=$(curl -s -o /dev/null -w "%{http_code}" \
            https://staging-api.myservice.com/health)
          if [ "$HEALTH" != "200" ]; then
            echo "헬스 체크 실패: HTTP $HEALTH"
            exit 1
          fi
          echo "Staging 헬스 체크 통과: HTTP $HEALTH"

      - name: Slack Staging 배포 알림
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "${{ job.status == 'success' && '✅' || '❌' }} Staging 배포 ${{ job.status }}",
              "attachments": [{
                "color": "${{ job.status == 'success' && '#00b894' || '#e17055' }}",
                "fields": [
                  {"title": "환경", "value": "Staging", "short": true},
                  {"title": "이미지 태그", "value": "${{ needs.build.outputs.image-tag }}", "short": true},
                  {"title": "커밋", "value": "${{ github.event.head_commit.message }}", "short": false},
                  {"title": "URL", "value": "https://staging-api.myservice.com", "short": false}
                ]
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

  # ══════════════════════════════════════════════════════
  # 5단계: Production 배포 (수동 승인 필요)
  # ══════════════════════════════════════════════════════
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build, deploy-staging]
    environment:
      name: production                        # Required Reviewers 설정된 환경
      url: https://api.myservice.com

    steps:
      - uses: actions/checkout@v4

      - name: AWS 자격증명 설정
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          role-session-name: GitHubActions-Production-${{ github.run_id }}
          aws-region: ${{ env.AWS_REGION }}

      - name: 태스크 정의 다운로드
        run: |
          aws ecs describe-task-definition \
            --task-definition my-ai-service-production \
            --query taskDefinition \
            > task-definition.json

      - name: 이미지 URI 업데이트
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: app
          image: ${{ needs.build.outputs.image-uri }}

      - name: Production 배포
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: my-ai-service-production
          cluster: my-ai-cluster-production
          wait-for-service-stability: true
          wait-for-minutes: 15

      - name: Production 스모크 테스트
        run: |
          sleep 60
          HEALTH=$(curl -s -o /dev/null -w "%{http_code}" \
            https://api.myservice.com/health)
          if [ "$HEALTH" != "200" ]; then
            echo "Production 헬스 체크 실패: HTTP $HEALTH"
            exit 1
          fi
          echo "Production 헬스 체크 통과: HTTP $HEALTH"

      - name: Slack Production 배포 성공 알림
        if: success()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "✅ Production 배포 완료",
              "attachments": [{
                "color": "#00b894",
                "fields": [
                  {"title": "환경", "value": "Production", "short": true},
                  {"title": "이미지 태그", "value": "${{ needs.build.outputs.image-tag }}", "short": true},
                  {"title": "커밋", "value": "${{ github.event.head_commit.message }}", "short": false},
                  {"title": "배포자", "value": "${{ github.actor }}", "short": true},
                  {"title": "URL", "value": "https://api.myservice.com", "short": false},
                  {"title": "워크플로", "value": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}", "short": false}
                ]
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

      - name: Slack Production 배포 실패 긴급 알림
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "<!channel> ❌ Production 배포 실패 - 즉시 확인 필요",
              "attachments": [{
                "color": "#e17055",
                "fields": [
                  {"title": "환경", "value": "Production", "short": true},
                  {"title": "이미지 태그", "value": "${{ needs.build.outputs.image-tag }}", "short": true},
                  {"title": "담당자", "value": "${{ github.actor }}", "short": true},
                  {"title": "워크플로 로그", "value": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}", "short": false}
                ]
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_EMERGENCY }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

### 프로젝트 디렉토리 구조

위 워크플로들이 동작하려면 다음 구조가 필요합니다.

```
project-root/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # PR 시 CI 실행
│   │   ├── docker-build.yml          # Docker 빌드 전용
│   │   ├── pipeline.yml              # 통합 파이프라인
│   │   └── reusable-deploy.yml       # 재사용 워크플로
│   └── actions/
│       └── setup-python-poetry/
│           └── action.yml            # Composite Action
├── src/
│   └── myapp/
│       ├── main.py
│       ├── api/
│       └── services/
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

### Slack 알림 설정 방법

1. **Slack Incoming Webhook 생성**: Slack 워크스페이스 → Apps → Incoming Webhooks → Add Configuration
2. **채널 선택**: `#deployments` 또는 `#alerts` 채널 권장
3. **Webhook URL 복사**: `https://hooks.slack.com/services/T.../B.../...` 형태
4. **GitHub Secrets 저장**: 저장소 Settings → Secrets and variables → Actions → New secret
   - `SLACK_WEBHOOK_URL`: 일반 배포 알림용
   - `SLACK_WEBHOOK_URL_EMERGENCY`: Production 실패 긴급 알림용

> **핵심 포인트:** `<!channel>`을 Slack 메시지에 포함하면 채널의 모든 멤버에게 알림이 전송됩니다. Production 실패 알림에만 이 태그를 사용하고, 일반 알림에는 사용하지 않아야 알림 피로를 방지할 수 있습니다.

---

## 8. 핵심 정리

### 워크플로 설계 체크리스트

팀 프로젝트에서 GitHub Actions 워크플로를 설계할 때 반드시 확인해야 할 항목입니다.

#### CI 워크플로 체크리스트

| 체크 항목 | 이유 | 구현 방법 |
|-----------|------|-----------|
| `paths:` 필터 설정 | 불필요한 워크플로 실행 방지 | `paths: ['src/**', 'tests/**']` |
| `concurrency` 설정 | 동일 브랜치 중복 실행 취소 | `cancel-in-progress: true` |
| pip 캐시 설정 | 빌드 시간 단축 | `actions/cache@v4` 또는 `cache: 'pip'` |
| 테스트 커버리지 요구 | 코드 품질 기준 | `--cov-fail-under=70` |
| PR 결과 댓글 자동화 | 리뷰어가 결과를 빠르게 파악 | `dorny/test-reporter`, `py-cov-action` |
| 아티팩트 보존 기간 | 스토리지 비용 관리 | `retention-days: 7` |
| `timeout-minutes` 설정 | 무한 실행 방지 | 잡 또는 스텝 단위 설정 |
| matrix 최소화 | 불필요한 빌드 분 절약 | 핵심 조합만 유지 |

#### 배포 워크플로 체크리스트

| 체크 항목 | 이유 | 구현 방법 |
|-----------|------|-----------|
| OIDC 인증 사용 | 장기 자격증명 제거 | `aws-actions/configure-aws-credentials` |
| 환경별 승인 게이트 | Production 배포 안전성 | GitHub Environments + Required Reviewers |
| 스모크 테스트 | 배포 후 기본 동작 확인 | 헬스 체크 엔드포인트 호출 |
| `wait-for-service-stability` | 배포 완료 확인 | ECS deploy action 옵션 |
| 성공/실패 Slack 알림 | 팀 즉각 인지 | `slackapi/slack-github-action` |
| 이미지 태그 전략 | 롤백 가능성 확보 | 날짜+SHA 태그 조합 |
| `concurrency` (비취소) | 배포는 중간에 취소 금지 | `cancel-in-progress: false` |
| Job 출력값 전달 | 이미지 태그 하위 잡에 전달 | `outputs:` + `needs.job.outputs` |

### 보안 체크리스트

| 보안 항목 | 나쁜 예 | 좋은 예 |
|-----------|--------|--------|
| **자격증명 관리** | Access Key를 워크플로에 하드코딩 | GitHub Secrets + OIDC |
| **권한 최소화** | `permissions: write-all` | 필요한 권한만 명시 |
| **서드파티 액션** | `uses: unknown/action@main` | `uses: unknown/action@v1.2.3` (태그 고정) |
| **환경 분리** | staging/production 동일 시크릿 | Environment Secrets로 분리 |
| **PR 이벤트** | `pull_request_target`으로 포크 PR 처리 | `pull_request`와 격리하여 처리 |
| **시크릿 노출** | `run: echo ${{ secrets.API_KEY }}` | `env:` 변수로 간접 참조 |
| **의존성 고정** | `pip install fastapi` | `pip install fastapi==0.111.0` |

### 이번 모듈에서 배운 것

이 모듈에서는 GitHub Actions를 활용한 실전 CI/CD 파이프라인 구축 전 과정을 다뤘습니다.

**개념 이해**: 워크플로, 이벤트, 잡, 스텝, 액션, 러너의 계층 구조와 동작 원리를 이해했습니다.

**CI 자동화**: Python 프로젝트에서 Ruff, Black, mypy, pytest를 자동으로 실행하는 완전한 CI 워크플로를 작성했습니다. Matrix 전략으로 여러 Python 버전을 동시에 테스트하고, 캐시로 빌드 시간을 단축하는 방법을 배웠습니다.

**Docker 빌드**: ECR에 이미지를 푸시하는 전체 과정을 자동화했습니다. OIDC 인증으로 장기 자격증명 없이 AWS에 안전하게 인증하는 방법을 익혔습니다.

**AWS 배포**: ECS 서비스를 업데이트하고 배포 완료를 대기하는 방법을 학습했습니다. IAM 신뢰 정책 JSON으로 GitHub Actions에 최소 권한을 부여하는 보안 설정도 실습했습니다.

**고급 기능**: 재사용 워크플로, Composite Actions, GitHub Environments의 승인 게이트, Repository/Environment Secrets 구분, 비용 관리 방법을 배웠습니다.

**실전 통합**: FastAPI AI 서비스의 feature 브랜치부터 Production 배포까지 전 과정을 하나의 파이프라인으로 통합했습니다. Slack 알림으로 팀이 배포 상황을 실시간으로 인지하는 모니터링 체계도 구축했습니다.

### 다음 단계

GitHub Actions 파이프라인을 완성했다면, 이제 팀 프로젝트의 마지막 관문인 프로젝트 주제 선정과 평가 기준을 확인할 차례입니다.

다음 문서 **[07_project_topics_and_evaluation.md](./07_project_topics_and_evaluation.md)**에서는 다음 내용을 다룹니다.

- **프로젝트 주제 가이드라인**: 45일 과정에서 완성 가능한 AI 서비스의 범위와 복잡도 기준
- **평가 루브릭**: 기술 구현, 협업 과정, 발표, 코드 품질 각 영역의 세부 평가 기준
- **발표 준비**: 데모 시나리오 작성, 기술 스택 설명, 트러블슈팅 사례 정리 방법
- **포트폴리오 정리**: GitHub 저장소를 채용 담당자가 보는 포트폴리오로 만드는 방법
- **우수 프로젝트 예시**: 이전 기수의 성공 사례와 실패 사례 분석

지금까지 배운 Git 브랜치 전략, 이슈 관리, GitHub Actions CI/CD 파이프라인을 팀 프로젝트에 모두 적용하면, 여러분의 프로젝트는 단순한 토이 프로젝트가 아닌 **실제 서비스 수준의 개발 프로세스**를 갖춘 결과물이 됩니다. 45일 과정의 마지막을 멋지게 마무리하세요.

---
