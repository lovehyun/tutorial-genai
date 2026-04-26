# 개발 환경 셋업 가이드

> 실습에 필요한 모든 도구를 설치하고 설정합니다.

---

## 설치 순서 개요

```mermaid
flowchart LR
    A["1. Python<br/>3.10+"] --> B["2. VS Code<br/>에디터"]
    B --> C["3. Git<br/>형상관리"]
    C --> D["4. Node.js<br/>18+"]
    D --> E["5. API 키<br/>발급"]
    E --> F["6. 가상환경<br/>& 패키지"]

    style A fill:#3776AB,stroke:#FFD43B,color:#fff
    style B fill:#007ACC,stroke:#005A9E,color:#fff
    style C fill:#F05032,stroke:#DE4C36,color:#fff
    style D fill:#68A063,stroke:#3C873A,color:#fff
    style E fill:#e17055,stroke:#d63031,color:#fff
    style F fill:#00b894,stroke:#00cec9,color:#fff
```

---

## 1. Python 설치

### Python 패키지/환경 관리 도구의 진화

Python 생태계에서 패키지 관리 도구는 시대에 따라 발전해왔습니다.

```mermaid
timeline
    title Python 패키지/환경 관리 도구의 진화
    1991~2000 : Python 탄생
               : 패키지 관리 없음
               : 수동으로 라이브러리 복사
    2004~2008 : easy_install 등장 (setuptools)
               : pip 등장 (2008)
               : PyPI 저장소 활성화
    2007~2012 : virtualenv 등장 (2007)
               : 프로젝트별 격리 환경 가능
               : Anaconda 등장 (2012)
    2012~2016 : Anaconda 전성기
               : 데이터 과학 붐과 함께 폭발적 성장
               : conda = 패키지 + 환경 + Python 관리
               : 단점: 용량 5GB, 느린 의존성 해결
    2017~2020 : Miniconda 부상
               : Anaconda가 너무 무겁다는 반발
               : 필요한 것만 설치하는 경량 conda
               : Pipenv, Poetry 등 대안 등장
    2021~2023 : venv가 Python 표준 내장 (3.3~)
               : pip + venv 조합이 공식 추천
               : Poetry/PDM 등 차세대 도구 경쟁
    2024~현재 : uv 등장 (2024.02, Astral)
              : Rust 기반 초고속 (pip 대비 10~100배)
              : pip + venv + pyenv + pip-compile 올인원 대체
              : 2025~2026 사실상 표준으로 자리잡음
```

```mermaid
flowchart TB
    A["수동 복사<br/>(~2004)"] --> B["pip<br/>(2008)"]
    B --> C["virtualenv<br/>(2007)"]
    C --> D["Anaconda<br/>(2012)"]
    D --> E["Miniconda<br/>(~2017)"]
    E --> F["pip + venv<br/>(~2021)"]
    F --> G["⚡ uv<br/>(2024~)"]

    style A fill:#2d3436,stroke:#636e72,color:#fff
    style B fill:#636e72,stroke:#b2bec3,color:#fff
    style C fill:#636e72,stroke:#b2bec3,color:#fff
    style D fill:#44A833,stroke:#2D7A1E,color:#fff
    style E fill:#44A833,stroke:#2D7A1E,color:#fff
    style F fill:#3776AB,stroke:#FFD43B,color:#fff
    style G fill:#DE5FE9,stroke:#9B30FF,color:#fff
```

| 시대 | 도구 | 문제점 → 다음 도구가 등장한 이유 |
|------|------|--------------------------------|
| ~2004 | 수동 복사 | 패키지 공유/설치가 너무 불편 |
| 2008~ | **pip** | 패키지 설치는 되지만 프로젝트 간 충돌 발생 |
| 2007~ | **virtualenv** | 가상환경 해결, 하지만 별도 설치 필요 + 과학 패키지(numpy 등) 설치 어려움 |
| 2012~ | **Anaconda** | 과학 패키지 원클릭! 하지만 **5GB 용량**, 느린 의존성 해결 |
| 2017~ | **Miniconda** | 경량화! 하지만 여전히 conda와 pip 혼용 시 환경 깨짐 |
| 2021~ | **pip + venv** | Python 공식 표준, 하지만 느리고 lockfile 없음 |
| 2024~ | **uv** | **Rust 기반 초고속**, pip 호환, 올인원 통합 → **현재 표준** |

---

### Python 배포판 종류

위 역사를 거쳐 현재는 여러 설치 방법이 공존합니다. 각각의 차이를 이해하고 상황에 맞게 선택하세요.

```mermaid
flowchart LR
    P["Python 설치 방법"]
    P --> A["🐍 네이티브 Python<br/>(python.org)"]
    P --> B["🟢 Anaconda"]
    P --> C["🔵 Miniconda"]
    P --> U["⚡ uv<br/>(Astral)"]

    U --> U1["Python 설치 + 패키지 관리<br/>+ 가상환경 + 프로젝트 관리<br/>올인원, 초고속 (Rust 기반)"]
    A --> A1["공식 CPython<br/>가장 기본적인 설치"]
    B --> B1["Python + 250개 패키지<br/>+ conda 패키지 관리자<br/>+ Jupyter, Spyder 등"]
    C --> C1["Python + conda만<br/>필요한 것만 직접 설치"]

    style U fill:#DE5FE9,stroke:#9B30FF,color:#fff
    style A fill:#3776AB,stroke:#FFD43B,color:#fff
    style B fill:#44A833,stroke:#2D7A1E,color:#fff
    style C fill:#44A833,stroke:#2D7A1E,color:#fff
```

### 배포판 비교

| 구분 | uv | 네이티브 Python | Anaconda | Miniconda |
|------|-----|----------------|----------|-----------|
| **설치 크기** | ~30MB | ~50MB | **~5GB** | ~200MB |
| **Python 포함** | `uv python install`로 설치 | 직접 설치 | 포함 | 포함 |
| **패키지 관리자** | `uv` (pip 호환) | `pip` | `conda` + `pip` | `conda` + `pip` |
| **가상환경** | `uv venv` (내장) | `venv` | `conda env` | `conda env` |
| **속도** | **10~100배 빠름** (Rust) | 기본 | 보통 | 보통 |
| **lockfile** | `uv.lock` 자동 생성 | 없음 (pip freeze) | environment.yml | environment.yml |
| **추천 대상** | **모든 Python 개발** | 전통적 방식 선호 시 | 데이터 과학 입문자 | 데이터 과학 경험자 |
| **등장 시기** | 2024~ (현재 표준) | 1991~ | 2012~ | 2014~ |

```
⚡ 본 과정 추천: uv

   이유:
   - 2025~2026년 현재 Python 생태계의 사실상 표준
   - Python 설치 + 패키지 관리 + 가상환경을 하나로 통합
   - pip보다 10~100배 빠름 (Rust 기반)
   - pip의 모든 명령어와 호환 (전환 부담 없음)
   - Ruff(린터)를 만든 Astral 팀이 개발 → 커뮤니티 신뢰도 높음

   만약 이미 Anaconda/Miniconda가 설치되어 있다면
   그대로 사용해도 됩니다. pip도 여전히 잘 동작합니다.
```

---

### 1-1. uv 설치 (추천)

**uv**는 Rust로 만든 **초고속 Python 패키지 관리자**입니다. Python 설치, 패키지 관리, 가상환경, 프로젝트 관리를 **하나의 도구로 통합**합니다.

> pip, pip-compile, pyenv, venv, virtualenv를 모두 대체하는 단일 도구

#### uv가 뭔가요?

```mermaid
flowchart LR
    subgraph 기존방식 ["기존 방식 (여러 도구 필요)"]
        direction TB
        A1["pyenv<br/>(Python 버전 관리)"]
        A2["pip<br/>(패키지 설치)"]
        A3["venv<br/>(가상환경)"]
        A4["pip-compile<br/>(의존성 잠금)"]
    end

    subgraph uv방식 ["uv (하나로 통합)"]
        B1["⚡ uv<br/>Python 설치<br/>+ 패키지 관리<br/>+ 가상환경<br/>+ lockfile<br/>+ 스크립트 실행"]
    end

    style 기존방식 fill:#ff6b6b11,stroke:#c0392b
    style uv방식 fill:#00b89411,stroke:#00b894
    style B1 fill:#DE5FE9,stroke:#9B30FF,color:#fff
```

#### 설치 방법

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew (Mac)
brew install uv

# 설치 확인
uv --version        # uv 0.6.x
```

#### uv로 Python 설치

uv는 Python 자체도 설치/관리할 수 있습니다.

```bash
# 사용 가능한 Python 버전 목록
uv python list

# Python 3.12 설치
uv python install 3.12

# 설치된 Python 확인
uv python list --only-installed

# 특정 버전으로 실행
uv run --python 3.12 python --version
```

#### uv 핵심 명령어

```bash
# 가상환경 생성 (pip의 python -m venv 대체)
uv venv

# 가상환경 활성화 (동일)
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 패키지 설치 (pip install 대체, 10~100배 빠름!)
uv pip install flask openai anthropic

# requirements.txt로 설치
uv pip install -r requirements.txt

# 설치된 패키지 목록
uv pip list

# 패키지 목록 저장
uv pip freeze > requirements.txt
```

#### uv 프로젝트 모드 (고급)

uv는 프로젝트 단위 관리도 지원합니다.

```bash
# 새 프로젝트 초기화 (pyproject.toml 생성)
uv init my-project
cd my-project

# 패키지 추가 (자동으로 pyproject.toml + uv.lock 업데이트)
uv add flask
uv add openai
uv add anthropic

# 스크립트 실행 (가상환경 자동 생성/활성화)
uv run python app.py

# 의존성 동기화 (다른 PC에서 동일 환경 재현)
uv sync
```

```
💡 처음엔 uv pip 명령어로 시작하세요!
   기존 pip과 동일한 방식이라 전환 부담이 없습니다.
   익숙해지면 uv add / uv run 프로젝트 모드를 사용해보세요.
```

#### pip vs uv 명령어 대응표

| 기존 (pip) | uv | 비고 |
|-----------|-----|------|
| `python -m venv venv` | `uv venv` | 가상환경 생성 |
| `pip install flask` | `uv pip install flask` | 패키지 설치 |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` | 일괄 설치 |
| `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` | 패키지 목록 저장 |
| `pip list` | `uv pip list` | 설치 목록 |
| `pip uninstall flask` | `uv pip uninstall flask` | 패키지 제거 |
| `pyenv install 3.12` | `uv python install 3.12` | Python 버전 설치 |

---

### 1-2. 네이티브 Python 설치

공식 [python.org](https://www.python.org/)에서 배포하는 **CPython**입니다. uv를 사용하면 `uv python install`로 설치할 수 있지만, 직접 설치하는 전통적 방법도 알아둡니다.

#### Windows

1. [python.org/downloads](https://www.python.org/downloads/) 에서 **Python 3.12** 다운로드
2. 설치 시 **반드시 "Add Python to PATH" 체크** (가장 중요!)

```
┌─────────────────────────────────────────────┐
│  Install Python 3.12.x                      │
│                                             │
│  ☑ Install launcher for all users           │
│  ☑ Add Python 3.12 to PATH  ← 반드시 체크! │
│                                             │
│  [Install Now]                              │
└─────────────────────────────────────────────┘
```

3. 설치 완료 후 **새 터미널**을 열어 확인:

```bash
python --version    # Python 3.12.x
pip --version       # pip 24.x
```

> "Add Python to PATH"를 체크하지 않았다면? 아래 **환경변수 설정** 섹션을 참고하세요.

#### Windows 환경변수 (PATH)란?

환경변수는 **운영체제가 프로그램을 찾는 경로 목록**입니다. `python`이라고 입력했을 때 실제 `python.exe` 파일이 어디 있는지 알려주는 역할입니다.

```
"python"을 입력하면...

  PATH에 등록되어 있을 때:
    → C:\Users\사용자\AppData\Local\Programs\Python\Python312\python.exe 실행! ✅

  PATH에 없을 때:
    → 'python'은(는) 내부 또는 외부 명령... 으로 인식되지 않습니다. ❌
```

#### 사용자 환경변수 vs 시스템 환경변수

Windows 환경변수 편집 화면을 열면 **두 개의 영역**이 보입니다.

```
┌──────────────────────────────────────────────────────────────┐
│  환경 변수                                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  < 사용자 변수 (사용자명) >                            │    │
│  │                                                      │    │
│  │  Path    C:\Users\사용자\AppData\Local\Programs\...  │    │
│  │  ...                                                 │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  < 시스템 변수 >                                      │    │
│  │                                                      │    │
│  │  Path    C:\Program Files\Git\cmd\...               │    │
│  │  ...                                                 │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [확인]  [취소]                                               │
└──────────────────────────────────────────────────────────────┘
```

| 구분 | 사용자 환경변수 | 시스템 환경변수 |
|------|---------------|---------------|
| **적용 범위** | 현재 로그인한 사용자만 | PC의 **모든 사용자** |
| **수정 권한** | 일반 사용자도 수정 가능 | **관리자 권한** 필요 |
| **설치 위치** | `C:\Users\사용자\...` | `C:\Program Files\...` |
| **우선순위** | PATH 검색 시 **먼저** 확인 | 사용자 변수 이후 확인 |
| **초기화** | 사용자 프로필 삭제 시 제거 | OS 재설치 전까지 유지 |

#### 주요 소프트웨어의 환경변수 등록 위치

각 프로그램의 설치 방식에 따라 환경변수 등록 위치가 다릅니다.

| 소프트웨어 | 환경변수 위치 | 이유 |
|-----------|-------------|------|
| **Git** | 시스템 변수 | `C:\Program Files\Git`에 설치 → 모든 사용자가 사용 |
| **Node.js** | 시스템 변수 | `C:\Program Files\nodejs`에 설치 → 전역 도구 |
| **Python** (공식 설치) | 사용자 변수 | `C:\Users\사용자\AppData\Local\...`에 설치 |
| **Anaconda** | 사용자 변수 | 사용자 홈 디렉토리에 설치 → 사용자별 관리 |
| **uv** | 사용자 변수 | `~\.cargo\bin`에 설치 → Rust 도구 체인 |
| **VS Code** | 시스템 변수 | `C:\Program Files\...`에 설치 (옵션 선택 시) |
| **Java (JDK)** | 시스템 변수 | 전역 런타임으로 설치되는 것이 일반적 |

> **핵심 포인트:** 프로그램이 `C:\Program Files\`에 설치되면 **시스템 변수**에, `C:\Users\사용자\` 아래에 설치되면 **사용자 변수**에 PATH가 등록됩니다. 대부분의 설치 프로그램이 자동으로 적절한 위치에 추가합니다.

```
💡 "Install for all users"를 선택하면 → 시스템 변수 (관리자 권한 필요)
   "Install for me only"를 선택하면 → 사용자 변수

   Python 설치 시 "Install for all users"를 체크하면
   C:\Program Files에 설치되고 시스템 변수에 등록됩니다.
```

#### 사용자 변수와 시스템 변수의 PATH 합치기

Windows는 실제로 프로그램을 찾을 때 두 PATH를 **합쳐서** 검색합니다.

```
최종 검색 순서:
  1. 사용자 변수의 Path (먼저 검색)
  2. 시스템 변수의 Path (나중에 검색)

예: 사용자 변수에 Python 3.12, 시스템 변수에 Python 3.10이 있으면
    → python 명령어는 3.12가 실행됨 (사용자 변수가 우선)
```

> 같은 프로그램이 두 군데 있으면 **사용자 변수가 우선**합니다. Anaconda를 설치했더니 기존 Python이 안 잡히는 경우가 이런 이유입니다.

#### 환경변수 수동 설정 방법 (PATH 미등록 시)

```
1. 시작 메뉴 → "환경 변수" 검색 → "시스템 환경 변수 편집" 클릭

2. [환경 변수(N)...] 버튼 클릭

3. "사용자 변수" 또는 "시스템 변수"에서 Path 선택 → [편집]

   ┌──────────────────────────────────────────────────┐
   │  환경 변수 편집                                   │
   │                                                  │
   │  C:\Users\사용자\AppData\Local\Programs\          │
   │    Python\Python312\                              │
   │  C:\Users\사용자\AppData\Local\Programs\          │
   │    Python\Python312\Scripts\                      │
   │                                                  │
   │  [새로 만들기]  [편집]  [삭제]                     │
   └──────────────────────────────────────────────────┘

4. 위 두 경로를 추가 → [확인]

5. 터미널을 새로 열어서 확인 (기존 터미널은 반영 안됨!)
```

```
💡 uv, Git, Node.js 등도 동일한 원리입니다.
   "명령어가 인식되지 않습니다" 오류가 나면
   해당 프로그램의 설치 경로가 PATH에 있는지 확인하세요.
```

#### Mac

```bash
# Homebrew가 없다면 먼저 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python@3.12

python3 --version
pip3 --version
```

> Mac에서는 `python3`, `pip3` 명령어를 사용합니다. (`python`은 시스템 기본 2.x일 수 있음)

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

python3 --version
pip3 --version
```

---

### 1-3. Anaconda 설치 (데이터 과학 올인원)

**Anaconda**는 Python + 250개 이상의 데이터 과학 패키지를 한 번에 설치합니다.

```
포함되는 것들:
- Python 3.12
- NumPy, Pandas, Matplotlib, Scikit-learn
- Jupyter Notebook / JupyterLab
- Spyder IDE
- conda 패키지 관리자
- 그 외 250개+ 패키지
```

#### 설치 방법

1. [anaconda.com/download](https://www.anaconda.com/download) 에서 다운로드
2. 설치 진행 (기본 설정 그대로 OK)
3. 설치 후 **Anaconda Prompt** (Windows) 또는 터미널에서 확인:

```bash
conda --version     # conda 24.x
python --version    # Python 3.12.x
```

#### conda 기본 명령어

```bash
# 패키지 설치 (pip 대신 conda 사용)
conda install numpy pandas matplotlib

# 가상환경 생성
conda create -n myenv python=3.12

# 가상환경 활성화
conda activate myenv

# 가상환경 비활성화
conda deactivate

# 설치된 환경 목록
conda env list
```

---

### 1-4. Miniconda 설치 (경량 conda)

**Miniconda**는 conda + Python만 포함한 최소 설치 버전입니다. 필요한 패키지만 직접 설치합니다.

#### 설치 방법

1. [docs.anaconda.com/miniconda](https://docs.anaconda.com/miniconda/) 에서 다운로드
2. 설치 후 확인:

```bash
conda --version     # conda 24.x
python --version    # Python 3.12.x
```

#### 어떤 도구를 선택할까?

```mermaid
flowchart TB
    Q["Python으로 뭘 하려고?"]
    Q -->|"이 과정 수강<br/>웹 개발, API, AI"| U["uv ✅ 추천"]
    Q -->|"데이터 과학 입문<br/>일단 다 설치하고 시작"| B["Anaconda"]
    Q -->|"데이터 과학<br/>필요한 것만 설치"| C["Miniconda"]
    Q -->|"전통적 방식<br/>pip이 익숙함"| A["네이티브 Python + pip"]

    style U fill:#DE5FE9,stroke:#9B30FF,color:#fff
    style A fill:#3776AB,stroke:#FFD43B,color:#fff
    style B fill:#44A833,stroke:#2D7A1E,color:#fff
    style C fill:#44A833,stroke:#2D7A1E,color:#fff
```

---

### 1-5. 패키지 관리자 비교 (uv vs pip vs conda)

| 구분 | uv | pip | conda |
|------|-----|-----|-------|
| **속도** | **10~100배 빠름** | 기본 | 보통 |
| **설치 대상** | Python 패키지 (PyPI) | Python 패키지 (PyPI) | Python + C/C++ 라이브러리 |
| **패키지 소스** | PyPI | PyPI | Anaconda 저장소 |
| **의존성 잠금** | `uv.lock` 자동 | `pip freeze` 수동 | `environment.yml` |
| **Python 버전 관리** | `uv python install` | 불가 | 가능 |
| **가상환경** | `uv venv` (내장) | `venv` (별도) | `conda env` (내장) |
| **실행** | `uv pip install flask` | `pip install flask` | `conda install flask` |

```
⚠️ 주의: conda 환경에서는 conda install을 먼저 시도하고,
          conda에 없는 패키지만 pip install로 설치하세요.
          pip과 conda를 무분별하게 섞으면 환경이 깨질 수 있습니다.

          uv는 pip과 100% 호환되므로 기존 pip 프로젝트에서
          그대로 전환할 수 있습니다.
```

---

## 2. VS Code 설치 및 설정

### 설치

[code.visualstudio.com](https://code.visualstudio.com/) 에서 다운로드 및 설치

### 필수 확장 프로그램 (Extensions)

| 확장 프로그램 | 용도 |
|--------------|------|
| **Python** (Microsoft) | Python 개발 지원 |
| **Pylance** (Microsoft) | Python 자동완성/타입 체크 |
| **HTML CSS Support** | HTML/CSS 자동완성 |
| **Live Server** | HTML 실시간 미리보기 |
| **Prettier** | 코드 자동 포맷팅 |
| **GitLens** | Git 히스토리 시각화 |
| **Markdown Preview Mermaid Support** | Mermaid 다이어그램 미리보기 |
| **REST Client** | API 테스트 도구 |

### VS Code 설치 후 확장 프로그램 일괄 설치 (터미널)

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ecmel.vscode-html-css
code --install-extension ritwickdey.LiveServer
code --install-extension esbenp.prettier-vscode
code --install-extension eamodio.gitlens
code --install-extension bierner.markdown-mermaid
code --install-extension humao.rest-client
```

### 추천 설정 (settings.json)

VS Code에서 `Ctrl+Shift+P` → `Preferences: Open Settings (JSON)`:

```json
{
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.formatOnSave": true,
    "editor.wordWrap": "on",
    "python.defaultInterpreterPath": "python3",
    "terminal.integrated.fontSize": 13,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000
}
```

---

## 3. Git 설치 및 설정

### 설치

- **Windows**: [git-scm.com](https://git-scm.com/) 에서 다운로드
- **Mac**: `brew install git`
- **Linux**: `sudo apt install git`

### Windows 설치 시 주요 옵션 안내

Git for Windows 설치 마법사에서 여러 옵션을 선택해야 합니다. 대부분 기본값으로 OK이지만, 아래 화면들은 이해하고 넘어가세요.

#### 기본 에디터 선택

```
┌─────────────────────────────────────────────┐
│  Choosing the default editor used by Git    │
│                                             │
│  ○ Use Vim (the ubiquitous text editor)     │
│  ● Use Visual Studio Code as Git's default  │  ← 추천
│    editor                                   │
│  ○ Use Notepad++ as Git's default editor    │
│  ○ Use Notepad as Git's default editor      │
└─────────────────────────────────────────────┘

→ VS Code를 사용할 예정이므로 "Visual Studio Code" 선택 추천
  (기본값인 Vim은 초보자에게 어려움)
```

#### git pull 동작 방식 (중요!)

```
┌─────────────────────────────────────────────────┐
│  Choose the default behavior of 'git pull'      │
│                                                 │
│  ● Default (fast-forward or merge)              │  ← 기본값, 추천
│  ○ Rebase                                       │
│  ○ Only ever fast-forward                       │
└─────────────────────────────────────────────────┘
```

| 옵션 | 동작 | 설명 |
|------|------|------|
| **Default (fast-forward or merge)** | `git pull --ff` | 가능하면 fast-forward, 불가능하면 merge 커밋 생성. **초보자 추천** |
| **Rebase** | `git pull --rebase` | 내 커밋을 원격 커밋 위로 재배치. 히스토리가 깔끔하지만 충돌 해결이 복잡할 수 있음 |
| **Only ever fast-forward** | `git pull --ff-only` | fast-forward만 허용, 불가능하면 에러. 가장 안전하지만 수동 작업 필요 |

```mermaid
flowchart LR
    subgraph Default ["Default (fast-forward or merge) ✅ 추천"]
        D1["원격에 새 커밋이 있고<br/>내 커밋도 있을 때"]
        D2["→ Merge 커밋 자동 생성<br/>→ 양쪽 변경사항 합침"]
        D1 --> D2
    end

    subgraph Rebase ["Rebase"]
        R1["원격에 새 커밋이 있고<br/>내 커밋도 있을 때"]
        R2["→ 내 커밋을 원격 뒤로 이동<br/>→ 히스토리가 일직선"]
        R1 --> R2
    end

    subgraph FFOnly ["Only fast-forward"]
        F1["원격에 새 커밋이 있고<br/>내 커밋도 있을 때"]
        F2["→ 에러! 수동으로 해결<br/>→ 가장 안전하지만 번거로움"]
        F1 --> F2
    end

    style Default fill:#00b89411,stroke:#00b894
    style Rebase fill:#fdcb6e11,stroke:#f39c12
    style FFOnly fill:#ff6b6b11,stroke:#c0392b
```

> 처음 설치라면 **Default (fast-forward or merge)** 를 선택하세요. 나중에 변경 가능합니다.

#### 줄바꿈 처리 (line ending)

```
┌─────────────────────────────────────────────────────┐
│  Configuring the line ending conversions            │
│                                                     │
│  ● Checkout Windows-style, commit Unix-style        │  ← Windows 추천
│    line endings (core.autocrlf = true)              │
│  ○ Checkout as-is, commit Unix-style line           │  ← Mac/Linux 추천
│    endings (core.autocrlf = input)                  │
│  ○ Checkout as-is, commit as-is                     │
│    (core.autocrlf = false)                          │
└─────────────────────────────────────────────────────┘

Windows: CRLF(\r\n)  |  Mac/Linux: LF(\n)
→ 팀 협업 시 줄바꿈 문자가 달라 충돌이 생길 수 있음
→ Windows에서는 첫 번째 옵션으로 자동 변환 추천
```

#### 기타 옵션 (기본값 OK)

| 옵션 화면 | 추천 설정 |
|-----------|----------|
| PATH environment | **Git from the command line and also from 3rd-party software** (기본값) |
| SSH executable | **Use bundled OpenSSH** (기본값) |
| HTTPS transport | **Use the OpenSSL library** (기본값) |
| Credential helper | **Git Credential Manager** (기본값) |
| Extra options | **Enable file system caching** 체크 (기본값) |

### 초기 설정

설치 후 **터미널**에서 다음을 실행합니다:

```bash
# 사용자 정보 설정 (필수)
git config --global user.name "홍길동"
git config --global user.email "hong@example.com"

# 기본 브랜치명 설정
git config --global init.defaultBranch main

# git pull 동작 방식 (설치 시 선택한 것과 동일, 나중에 변경 가능)
git config --global pull.rebase false      # Default (merge)
# git config --global pull.rebase true     # Rebase 방식으로 변경하고 싶다면

# 한글 파일명 깨짐 방지
git config --global core.quotepath false

# 확인
git config --list
```

### GitHub 계정 생성

1. [github.com](https://github.com/) 에서 계정 생성
2. 실습 저장소 Fork 또는 Clone:

```bash
git clone https://github.com/[저장소주소]/tutorial-genai.git
cd tutorial-genai
```

### Git Credential (인증 정보) 관리

Git으로 GitHub에 처음 push/pull하면 로그인을 요청합니다. **Git Credential Manager**가 비밀번호를 저장해주므로 다음부터는 자동 로그인됩니다.

하지만 **계정을 변경하거나, 토큰이 만료**되었을 때는 저장된 인증 정보를 삭제해야 합니다.

#### Windows에서 Git Credential 삭제

```
방법 1: Windows 자격 증명 관리자 (GUI)

   제어판 → 사용자 계정 → 자격 증명 관리자
   (또는 시작 메뉴에서 "자격 증명 관리자" 검색)

   ┌──────────────────────────────────────────┐
   │  자격 증명 관리자                         │
   │                                          │
   │  [웹 자격 증명]  [Windows 자격 증명]      │
   │                                          │
   │  ▼ 일반 자격 증명                        │
   │    ├─ git:https://github.com  ← 이것!   │
   │    │   사용자 이름: your-username         │
   │    │   [편집]  [제거]  ← 제거 클릭       │
   │    └─ ...                                │
   └──────────────────────────────────────────┘

방법 2: 명령어로 삭제

   # 저장된 GitHub 인증 정보 삭제
   cmdkey /delete:git:https://github.com

   # 또는 Git 명령어로
   git credential-manager erase
   host=github.com
   protocol=https
   (Enter 두 번 입력)
```

#### Mac에서 Git Credential 삭제

```bash
# 키체인에서 GitHub 인증 정보 삭제
git credential-osxkeychain erase
host=github.com
protocol=https
# (Enter 두 번 입력)

# 또는 키체인 접근 앱 → github.com 검색 → 삭제
```

#### Linux에서 Git Credential 삭제

```bash
# credential store 사용 시 (평문 저장)
# ~/.git-credentials 파일에서 해당 줄 삭제

# credential cache 사용 시 (메모리 캐시)
git credential-cache exit
```

> 삭제 후 다음 push/pull 시 다시 로그인하면 새 인증 정보가 저장됩니다.

---

## 4. Node.js 설치 (일부 프로젝트용)

### 설치

- **Windows/Mac**: [nodejs.org](https://nodejs.org/) 에서 **LTS 버전** 다운로드
- **Linux**:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 확인

```bash
node --version     # v20.x
npm --version      # 10.x
```

---

## 5. API 키 발급

### OpenAI API Key

```mermaid
flowchart LR
    A["platform.openai.com<br/>회원가입"] --> B["API Keys 메뉴"]
    B --> C["Create new secret key"]
    C --> D["키 복사 후 안전하게 보관<br/>sk-xxxxxxxx"]

    style D fill:#e17055,stroke:#d63031,color:#fff
```

1. [platform.openai.com](https://platform.openai.com/) 접속 및 로그인
2. 좌측 메뉴 → **API Keys**
3. **"Create new secret key"** 클릭
4. 키를 **반드시 복사해서 저장** (다시 확인 불가)
5. 결제 수단 등록 (사용량 기반 과금)

### Anthropic (Claude) API Key

1. [console.anthropic.com](https://console.anthropic.com/) 접속 및 로그인
2. **API Keys** 메뉴
3. **"Create Key"** 클릭
4. 키 복사 후 보관

### Google (Gemini) API Key

1. [aistudio.google.com](https://aistudio.google.com/) 접속
2. **"Get API key"** 클릭
3. 키 복사 후 보관

### API 키 관리 방법 (.env 파일)

```bash
# 프로젝트 루트에 .env 파일 생성
touch .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxx
```

**주의: `.env` 파일은 절대로 Git에 올리지 않습니다!**

`.gitignore` 파일에 추가:
```
.env
```

---

## 6. Python 가상환경 & 패키지 설치

### 가상환경이란?

```mermaid
flowchart LR
    subgraph 가상환경없음 ["가상환경 없이 (위험)"]
        direction TB
        S["시스템 Python"]
        S --> P1["프로젝트A: flask 2.0"]
        S --> P2["프로젝트B: flask 3.0"]
        P1 -.->|"충돌!"| P2
    end

    subgraph 가상환경있음 ["가상환경 사용 (안전)"]
        direction TB
        V1["venv A"] --> PA["flask 2.0"]
        V2["venv B"] --> PB["flask 3.0"]
    end

    style 가상환경없음 fill:#ff6b6b11,stroke:#c0392b
    style 가상환경있음 fill:#00b89411,stroke:#00cec9
```

프로젝트별로 독립된 Python 환경을 만들어 패키지 충돌을 방지합니다.

### 방법 1: uv (추천)

```bash
# 프로젝트 폴더로 이동
cd tutorial-genai

# 가상환경 생성 (.venv 폴더 생성)
uv venv

# 활성화
# Windows:
.venv\Scripts\activate

# Mac/Linux:
source .venv/bin/activate

# 활성화 확인 → 프롬프트 앞에 (.venv) 표시
(.venv) $

# 비활성화
deactivate
```

### 방법 2: venv (네이티브 Python 사용 시)

```bash
cd tutorial-genai

# 가상환경 생성
python -m venv venv

# 활성화
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 활성화 확인 → 프롬프트 앞에 (venv) 표시
(venv) $

# 비활성화
deactivate
```

### 방법 3: conda env (Anaconda/Miniconda 사용 시)

```bash
# 가상환경 생성 (Python 버전 지정 가능)
conda create -n tutorial python=3.12

# 활성화
conda activate tutorial

# 활성화 확인 → 프롬프트 앞에 (tutorial) 표시
(tutorial) $

# 비활성화
conda deactivate

# 환경 목록 확인
conda env list

# 환경 삭제
conda env remove -n tutorial
```

### 가상환경 도구 비교

| 구분 | uv venv | venv | conda env |
|------|---------|------|-----------|
| **생성 속도** | **즉시** | 보통 | 느림 |
| **Python 버전** | 지정 가능 (`uv venv --python 3.12`) | 시스템 버전만 | 지정 가능 |
| **환경 위치** | `.venv/` (프로젝트 내) | `venv/` (프로젝트 내) | 중앙 관리 |
| **활성화** | 동일 (`source .venv/bin/activate`) | 동일 | `conda activate` |

```
본 과정에서는 uv를 사용합니다.
pip/venv 사용자는 동일한 방식으로 진행 가능합니다.
conda 사용자는 conda install로 대체하면 됩니다.
```

### 패키지 설치

```bash
# === uv 사용 시 (추천) ===
uv pip install python-dotenv requests flask
uv pip install openai anthropic
uv pip install langchain langchain-openai langchain-anthropic langgraph
uv pip install transformers torch sentence-transformers
uv pip install faiss-cpu chromadb
uv pip install pandas numpy

# === pip 사용 시 (동일한 패키지) ===
pip install python-dotenv requests flask
pip install openai anthropic
pip install langchain langchain-openai langchain-anthropic langgraph
pip install transformers torch sentence-transformers
pip install faiss-cpu chromadb
pip install pandas numpy

# 설치 확인
uv pip list    # 또는 pip list
```

### 패키지 목록 저장/복원

```bash
# uv 사용 시
uv pip freeze > requirements.txt
uv pip install -r requirements.txt

# pip 사용 시 (동일)
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## 7. 설치 확인 체크리스트

다음 명령어를 실행하여 모든 것이 정상인지 확인합니다:

```bash
# uv (추천 패키지 관리자)
uv --version                        # uv 0.6.x ✓

# Python
python --version                    # Python 3.12.x ✓

# pip (uv 미사용 시)
pip --version                       # pip 24.x ✓

# Git
git --version                       # git version 2.x ✓

# Node.js
node --version                      # v20.x ✓

# VS Code
code --version                      # 1.9x.x ✓

# Python 패키지 확인
python -c "import openai; print('OpenAI OK')"
python -c "import anthropic; print('Anthropic OK')"
python -c "import flask; print('Flask OK')"
python -c "import langchain; print('LangChain OK')"
```

### API 키 테스트

```python
# test_api.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI 테스트
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=10
)
print("OpenAI:", response.choices[0].message.content)

# Anthropic 테스트
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=10,
    messages=[{"role": "user", "content": "Hello!"}]
)
print("Claude:", response.content[0].text)
```

```bash
python test_api.py
# OpenAI: Hello! How can I...
# Claude: Hello! How can I...
```

---

## 8. 트러블슈팅

| 문제 | 해결 방법 |
|------|-----------|
| `python`이 인식 안 됨 | PATH 환경변수 설정 확인 (위 환경변수 섹션 참고) / `python3` 시도 |
| `uv`가 인식 안 됨 | 터미널을 새로 열기 / PATH에 `~/.cargo/bin` 확인 |
| `pip install` 권한 오류 | 가상환경 활성화 확인 / `uv pip install` 사용 |
| API 키 오류 | `.env` 파일 경로 및 키 형식 확인 |
| `ModuleNotFoundError` | 가상환경 활성화 후 `uv pip install` 재실행 |
| Git push 거부 | `.env` 파일이 포함되어 있지 않은지 확인 |
| Git push 시 인증 실패 | 저장된 credential 삭제 후 재로그인 (위 Git Credential 섹션 참고) |
| VS Code에서 Python 인터프리터 안 잡힘 | `Ctrl+Shift+P` → `Python: Select Interpreter` → `.venv` 선택 |
| "명령어가 인식되지 않습니다" | 해당 프로그램의 PATH 환경변수 등록 확인 후 터미널 재시작 |
