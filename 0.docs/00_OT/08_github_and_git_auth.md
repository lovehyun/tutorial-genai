# GitHub와 Git 인증

> "코드를 안전하게 주고받는 법" — GitHub 계정 설정부터 SSH 키 인증까지, Git의 원격 저장소 연동을 완전히 이해합니다

---

## 1. GitHub 시작하기

### GitHub이란?

**GitHub**은 Git 원격 저장소를 호스팅하는 클라우드 서비스입니다. 단순한 코드 저장소를 넘어, 전 세계 개발자들이 협업하는 **가장 큰 개발 플랫폼**입니다.

```mermaid
flowchart LR
    A["내 컴퓨터<br/>(Local Git)"] <-->|"push / pull"| B["GitHub<br/>(Remote)"]
    B <-->|"push / pull"| C["팀원 A<br/>(Local Git)"]
    B <-->|"push / pull"| D["팀원 B<br/>(Local Git)"]
    B --> E["CI/CD<br/>자동 배포"]
    B --> F["이슈 관리<br/>코드 리뷰"]

    style A fill:#74b9ff,stroke:#0984e3,color:#fff
    style B fill:#2d3436,stroke:#636e72,color:#fff
    style C fill:#74b9ff,stroke:#0984e3,color:#fff
    style D fill:#74b9ff,stroke:#0984e3,color:#fff
    style E fill:#55efc4,stroke:#00b894,color:#2d3436
    style F fill:#fdcb6e,stroke:#f39c12,color:#2d3436
```

GitHub이 제공하는 핵심 기능:

| 기능 | 설명 |
|------|------|
| **코드 저장소** | Git 원격 저장소 무료 호스팅 (Public/Private) |
| **협업** | Pull Request, 코드 리뷰, 브랜치 관리 |
| **이슈 관리** | 버그 리포트, 기능 요청, 작업 추적 |
| **CI/CD** | GitHub Actions로 자동 테스트/배포 |
| **포트폴리오** | 개발자의 이력서 역할 (잔디밭, 프로젝트) |
| **문서화** | Wiki, GitHub Pages로 문서/웹사이트 호스팅 |

> **핵심 포인트:** GitHub은 단순한 "코드 저장소"가 아니라, **개발자의 이력서이자 협업 플랫폼**입니다. 채용 담당자들이 지원자의 GitHub을 확인하는 것은 이제 일반적인 관행입니다.

---

### GitHub 계정 생성

#### Step 1: 가입

1. [github.com](https://github.com/) 접속
2. **"Sign up"** 클릭
3. 이메일 주소 입력
4. 비밀번호 설정 (15자 이상 또는 8자 이상 + 숫자/소문자 포함)
5. 사용자명(Username) 입력
6. 이메일 인증 코드 확인

#### Step 2: 사용자명 선정 팁

| 권장 | 비권장 |
|------|--------|
| 영문 소문자 + 숫자 | 한글, 특수문자 |
| 짧고 기억하기 쉬운 (예: `suhyun-park`) | 너무 긴 이름 (예: `my-super-awesome-dev-2024`) |
| 본명 또는 일관된 아이디 | 의미 없는 문자열 (예: `asdf1234qwer`) |
| 하이픈(`-`)으로 단어 구분 | 언더스코어(`_`)는 가능하나 하이픈이 일반적 |

#### Step 3: 프로필 설정

1. 우측 상단 아바타 클릭 → **Settings**
2. **Profile** 메뉴에서:
   - **Name**: 실명 또는 닉네임
   - **Bio**: 간단한 소개 (예: "풀스택 개발 수강생 | Python & AI")
   - **Avatar**: 프로필 사진 업로드
3. **프로필 README** (선택): `username/username` 이름의 저장소를 만들면, 그 안의 `README.md`가 프로필 페이지에 표시됩니다.

#### Step 4: 이메일 설정과 프라이버시

1. Settings → **Emails**
2. **Keep my email addresses private** 체크 권장
   - GitHub이 제공하는 noreply 이메일을 커밋에 사용
   - 형식: `12345678+username@users.noreply.github.com`
3. Git 설정에서 이 이메일 사용:

```bash
git config --global user.email "12345678+username@users.noreply.github.com"
```

---

### 저장소(Repository) 만들기

#### 새 저장소 생성 과정

1. GitHub 우측 상단 **"+"** → **"New repository"**
2. 저장소 설정:

```
┌─────────────────────────────────────────────────┐
│  Create a new repository                        │
│                                                 │
│  Repository name: [my-first-project          ]  │
│                                                 │
│  Description: [첫 번째 프로젝트              ]  │
│                                                 │
│  ● Public   ○ Private                           │
│                                                 │
│  ☑ Add a README file                            │
│  Add .gitignore: [Python          ▼]            │
│  Choose a license: [MIT License   ▼]            │
│                                                 │
│  [Create repository]                            │
└─────────────────────────────────────────────────┘
```

#### Public vs Private

| 구분 | Public | Private |
|------|--------|---------|
| **가시성** | 누구나 볼 수 있음 | 초대된 사람만 볼 수 있음 |
| **비용** | 무료 | 무료 (무제한) |
| **용도** | 오픈소스, 포트폴리오 | 개인 프로젝트, 회사 코드 |
| **GitHub Pages** | 무료 | 무료 (Pro 이상) |

#### 초기화 옵션

- **README.md**: 프로젝트 소개 문서. 체크하면 자동 생성
- **.gitignore**: Git이 추적하지 않을 파일 목록. 언어별 템플릿 제공 (Python, Node 등)
- **LICENSE**: 오픈소스 라이선스. MIT, Apache 2.0 등 선택 가능

#### 저장소 URL 구조

```
https://github.com/{username}/{repo-name}
                     ↑           ↑
                  사용자명    저장소 이름

예시: https://github.com/suhyun-park/tutorial-genai
```

---

## 2. git init vs git clone

프로젝트를 Git으로 관리하는 방법은 두 가지입니다: **처음부터 시작하기(init)** 또는 **기존 저장소 가져오기(clone)**.

### git init — 처음부터 시작하기

로컬에서 새 프로젝트를 시작할 때 사용합니다.

```bash
# 1. 프로젝트 폴더 생성 및 이동
mkdir my-project
cd my-project

# 2. Git 저장소 초기화 (.git 폴더 생성)
git init

# 3. 파일 생성 및 첫 커밋
echo "# My Project" > README.md
git add README.md
git commit -m "첫 번째 커밋"

# 4. GitHub에서 빈 저장소를 만든 후, 원격 저장소 연결
git remote add origin https://github.com/username/my-project.git

# 5. 첫 push (-u 옵션으로 upstream 설정)
git push -u origin main
```

**이미 존재하는 폴더**를 Git으로 관리하려면:

```bash
cd existing-project    # 기존 프로젝트 폴더로 이동
git init               # Git 저장소 초기화
git add .              # 모든 파일 스테이징
git commit -m "기존 프로젝트를 Git으로 관리 시작"
```

### git clone — 기존 저장소 가져오기

이미 GitHub에 있는 저장소를 로컬로 복제할 때 사용합니다.

```bash
# HTTPS로 클론
git clone https://github.com/username/my-project.git

# SSH로 클론
git clone git@github.com:username/my-project.git

# 특정 폴더 이름으로 클론
git clone https://github.com/username/my-project.git my-folder
```

`git clone`은 다음을 **자동으로** 수행합니다:
- 저장소 전체 히스토리 다운로드
- `origin`이라는 이름으로 원격 저장소 연결
- 기본 브랜치(main)로 체크아웃

### init vs clone 비교

| 구분 | `git init` | `git clone` |
|------|-----------|-------------|
| **사용 시점** | 새 프로젝트를 처음 시작할 때 | 기존 저장소를 가져올 때 |
| **원격 저장소** | 수동으로 `git remote add` 필요 | 자동으로 `origin` 설정 |
| **기존 커밋** | 없음 (빈 저장소) | 모든 히스토리 포함 |
| **대표 시나리오** | "내가 새 프로젝트를 만든다" | "팀 프로젝트에 참여한다" |

```mermaid
flowchart TB
    START["프로젝트 시작"] --> Q{"GitHub에<br/>저장소가<br/>이미 있나요?"}

    Q -->|"아니오<br/>(새 프로젝트)"| INIT["git init"]
    Q -->|"예<br/>(기존 저장소)"| CLONE["git clone URL"]

    INIT --> REMOTE["git remote add origin URL"]
    REMOTE --> PUSH["git push -u origin main"]
    PUSH --> DONE["원격 저장소 연동 완료"]

    CLONE --> DONE

    style START fill:#6c5ce7,stroke:#5f27cd,color:#fff
    style Q fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style INIT fill:#74b9ff,stroke:#0984e3,color:#fff
    style CLONE fill:#55efc4,stroke:#00b894,color:#2d3436
    style REMOTE fill:#74b9ff,stroke:#0984e3,color:#fff
    style PUSH fill:#74b9ff,stroke:#0984e3,color:#fff
    style DONE fill:#00b894,stroke:#00cec9,color:#fff
```

> **핵심 포인트:** 수업에서는 대부분 `git clone`을 사용합니다. 강사가 제공하는 저장소를 클론하여 실습을 진행하기 때문입니다. `git init`은 개인 프로젝트를 시작할 때 사용합니다.

---

## 3. 원격 저장소 연결 방식: HTTPS vs SSH

GitHub과 통신할 때, 두 가지 프로토콜을 사용할 수 있습니다.

### 두 가지 프로토콜

```bash
# HTTPS 방식
https://github.com/username/repo.git

# SSH 방식
git@github.com:username/repo.git
```

### HTTPS 방식

```
URL 형태: https://github.com/username/repo.git
포트: 443 (HTTPS 기본 포트)
인증: 사용자명 + Personal Access Token (PAT)
```

- 설정이 간단하고 직관적
- 대부분의 네트워크 환경에서 동작 (방화벽 친화적)
- 매번 인증이 필요하지만 Credential Manager로 해결 가능
- 초보자에게 추천하는 방식

### SSH 방식

```
URL 형태: git@github.com:username/repo.git
포트: 22 (SSH 기본 포트)
인증: SSH 키 쌍 (공개키/개인키)
```

- 초기 설정(키 생성 및 등록)이 필요
- 한 번 설정하면 비밀번호 입력 불필요
- 공개키 암호화 기반으로 더 안전
- 일부 네트워크에서 22번 포트가 차단될 수 있음

### HTTPS vs SSH 비교표

| 구분 | HTTPS | SSH |
|------|-------|-----|
| **URL 형태** | `https://github.com/user/repo.git` | `git@github.com:user/repo.git` |
| **인증 방식** | 사용자명 + PAT | SSH 키 쌍 |
| **설정 난이도** | 쉬움 | 중간 (키 생성 필요) |
| **보안** | 좋음 (PAT 기반) | 매우 좋음 (공개키 암호화) |
| **편의성** | Credential Manager 필요 | 한 번 설정하면 자동 인증 |
| **방화벽** | 대부분 통과 (443 포트) | 일부 차단 가능 (22 포트) |
| **추천 대상** | 입문자, 임시 환경 | 일상적 개발자, 장기 사용 |

```mermaid
sequenceDiagram
    participant Dev as 개발자
    participant Git as Git Client
    participant GH as GitHub

    Note over Dev,GH: HTTPS 인증 흐름
    Dev->>Git: git push
    Git->>GH: HTTPS 요청 (443 포트)
    GH-->>Git: 인증 요청
    Git-->>Dev: 사용자명/PAT 입력 요청
    Dev->>Git: 사용자명 + PAT 입력
    Git->>GH: 인증 정보 전송
    GH-->>Git: 인증 성공, push 완료

    Note over Dev,GH: SSH 인증 흐름
    Dev->>Git: git push
    Git->>GH: SSH 접속 (22 포트)
    GH-->>Git: 랜덤 챌린지 전송
    Git->>Git: 개인키로 챌린지 서명
    Git->>GH: 서명된 응답 전송
    GH->>GH: 등록된 공개키로 검증
    GH-->>Git: 인증 성공, push 완료
```

> **핵심 포인트:** 처음에는 HTTPS로 시작하고, Git에 익숙해지면 SSH로 전환하는 것을 추천합니다. 이 문서에서는 두 가지 모두 설정하는 방법을 다룹니다.

---

## 4. HTTPS 인증과 Credential Manager

### Personal Access Token (PAT)

GitHub은 **2021년 8월 13일**부터 비밀번호 인증을 중단했습니다. 대신 **Personal Access Token(PAT)** 을 사용해야 합니다.

#### PAT 생성 방법

1. GitHub 로그인 → 우측 상단 아바타 → **Settings**
2. 좌측 메뉴 맨 아래 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **"Generate new token"** → **"Generate new token (classic)"**

```
┌─────────────────────────────────────────────────┐
│  New personal access token (classic)            │
│                                                 │
│  Note: [내 노트북용 토큰            ]           │
│                                                 │
│  Expiration: [90 days           ▼]              │
│                                                 │
│  Select scopes:                                 │
│  ☑ repo         (저장소 전체 접근)              │
│  ☑ workflow     (GitHub Actions)                │
│  ☐ write:packages                               │
│  ☐ delete:packages                              │
│  ☐ admin:org                                    │
│  ☐ admin:public_key                             │
│  ...                                            │
│                                                 │
│  [Generate token]                               │
└─────────────────────────────────────────────────┘
```

5. 생성된 토큰을 **반드시 복사하여 안전한 곳에 저장** (다시 확인 불가!)
6. 토큰 형태: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

> **주의:** PAT은 비밀번호와 동일한 보안 수준입니다. 절대로 코드에 직접 넣거나 공개 저장소에 올리지 마세요.

#### PAT Scope 설명

| Scope | 설명 | 필수 여부 |
|-------|------|-----------|
| **repo** | Private 저장소를 포함한 전체 접근 | 필수 |
| **workflow** | GitHub Actions 워크플로 수정 | 권장 |
| **read:org** | 조직 멤버십 읽기 | 조직 사용 시 |
| **gist** | Gist 생성/수정 | 선택 |

---

### Git Credential Manager (GCM)

매번 PAT을 입력하는 것은 번거롭습니다. **Git Credential Manager**는 인증 정보를 OS의 보안 저장소에 안전하게 저장하여, 한 번 입력하면 다음부터 자동으로 인증합니다.

#### 설치 및 설정

```bash
# Windows: Git for Windows에 기본 포함 (추가 설치 불필요)
git config --global credential.helper manager

# Mac: Homebrew로 설치
brew install git-credential-manager
git config --global credential.helper osxkeychain

# Linux: GCM 설치 후 설정
git-credential-manager configure
git config --global credential.helper manager
```

### Credential 저장 방식 비교

| 방식 | 명령어 | 저장 위치 | 보안 | 특징 |
|------|--------|-----------|------|------|
| **manager** | `credential.helper manager` | OS 키체인 | 높음 | GCM 사용, **추천** |
| **store** | `credential.helper store` | `~/.git-credentials` (평문) | 낮음 | 파일에 평문 저장, 비추천 |
| **cache** | `credential.helper cache` | 메모리 | 중간 | 일정 시간 후 자동 삭제 |

#### OS별 기본 보안 저장소

| OS | 저장소 | 확인 방법 |
|----|--------|-----------|
| **Windows** | Windows 자격 증명 관리자 | 제어판 → 자격 증명 관리자 |
| **Mac** | Keychain Access | 키체인 접근 앱 |
| **Linux** | libsecret / GNOME Keyring | `secret-tool` 명령어 |

### Credential 관리: 저장된 인증 정보 확인/삭제

인증에 문제가 생겼을 때(계정 변경, 토큰 만료 등) 저장된 credential을 삭제해야 합니다.

#### Windows

```bash
# 방법 1: 명령어로 삭제
cmdkey /delete:git:https://github.com

# 방법 2: GUI
# 제어판 → 사용자 계정 → 자격 증명 관리자
# → Windows 자격 증명 → git:https://github.com → 제거
```

#### Mac

```bash
# 키체인에서 GitHub 인증 정보 삭제
git credential-osxkeychain erase
host=github.com
protocol=https
# (빈 줄에서 Enter)
```

#### Linux

```bash
# credential-store 사용 시 (평문 파일)
# ~/.git-credentials 파일에서 해당 줄 삭제

# credential-cache 사용 시
git credential-cache exit

# GCM 사용 시
git-credential-manager erase
host=github.com
protocol=https
# (빈 줄에서 Enter)
```

> **핵심 포인트:** "git push 시 인증 실패" 오류가 나면, **저장된 credential을 삭제하고 다시 로그인**하는 것이 가장 빠른 해결 방법입니다.

---

## 5. 공개키 암호화와 PKI 기초

SSH 인증을 이해하려면, 먼저 **공개키 암호화** 개념을 알아야 합니다.

### 대칭키 vs 비대칭키(공개키) 암호화

#### 대칭키 암호화

**같은 키** 하나로 암호화와 복호화를 모두 수행합니다.

- 비유: **금고 열쇠** — 열쇠 하나로 잠그고 열 수 있다
- 문제: 상대방에게 열쇠를 안전하게 전달하는 것이 어렵다
- 예시: AES, DES

#### 비대칭키(공개키) 암호화

**두 개의 키**(공개키 + 개인키)를 사용합니다.

- 공개키로 암호화 → 개인키로만 복호화 가능
- 개인키로 서명 → 공개키로 검증 가능
- 비유: **우체통** — 누구나 편지를 넣을 수 있지만(공개키), 열어볼 수 있는 건 주인뿐(개인키)
- 예시: RSA, Ed25519

**대칭키 암호화** — 같은 키 하나로 암호화/복호화

```mermaid
flowchart LR
    SA["평문<br/>Hello"] --> SB["암호화<br/>(키 A)"]
    SB --> SC["암호문<br/>X#8kQ"]
    SC --> SD["복호화<br/>(키 A)"]
    SD --> SE["평문<br/>Hello"]

    style SA fill:#74b9ff,stroke:#0984e3,color:#fff
    style SB fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style SC fill:#636e72,stroke:#2d3436,color:#fff
    style SD fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style SE fill:#74b9ff,stroke:#0984e3,color:#fff
```

**비대칭키(공개키) 암호화** — 공개키로 암호화, 개인키로 복호화

```mermaid
flowchart LR
    AA["평문<br/>Hello"] --> AB["암호화<br/>(공개키)"]
    AB --> AC["암호문<br/>X#8kQ"]
    AC --> AD["복호화<br/>(개인키)"]
    AD --> AE["평문<br/>Hello"]

    style AA fill:#74b9ff,stroke:#0984e3,color:#fff
    style AB fill:#55efc4,stroke:#00b894,color:#2d3436
    style AC fill:#636e72,stroke:#2d3436,color:#fff
    style AD fill:#e17055,stroke:#d63031,color:#fff
    style AE fill:#74b9ff,stroke:#0984e3,color:#fff
```

| 구분 | 대칭키 | 비대칭키 (공개키) |
|------|--------|-------------------|
| **키 개수** | 1개 (같은 키) | 2개 (공개키 + 개인키) |
| **속도** | 빠름 | 느림 |
| **키 전달 문제** | 있음 (키를 안전하게 전달해야 함) | 없음 (공개키는 공개해도 안전) |
| **용도** | 데이터 암호화 (AES) | 인증, 키 교환, 디지털 서명 |
| **비유** | 금고 열쇠 (하나) | 우체통 (넣는 건 누구나, 여는 건 주인만) |

---

### PKI (Public Key Infrastructure)

**PKI(공개키 기반 구조)** 는 공개키 암호화를 실제 세상에서 안전하게 운용하기 위한 체계입니다.

핵심 구성 요소:

| 구성 요소 | 설명 | 실생활 예시 |
|-----------|------|-------------|
| **공개키/개인키** | 암호화/서명에 사용하는 키 쌍 | SSH 키, GPG 키 |
| **인증서 (Certificate)** | 공개키의 진짜 주인을 증명하는 문서 | HTTPS SSL 인증서 |
| **인증기관 (CA)** | 인증서를 발급하는 신뢰된 기관 | Let's Encrypt, DigiCert |
| **디지털 서명** | 개인키로 서명 → 공개키로 검증 | Git 커밋 서명, 문서 서명 |

우리가 매일 사용하는 PKI 예시:
- **HTTPS**: 웹사이트의 SSL/TLS 인증서 (브라우저 주소창의 자물쇠 아이콘)
- **SSH**: 서버 접속 시 키 기반 인증
- **코드 서명**: 앱 배포 시 개발자 신원 확인

---

### SSH 인증의 원리

SSH 키 인증은 "**나는 이 공개키의 주인이다**"를 증명하는 과정입니다.

```mermaid
sequenceDiagram
    participant Client as 클라이언트 (내 PC)
    participant Server as 서버 (GitHub)

    Client->>Server: 1. SSH 접속 요청
    Note right of Server: 등록된 공개키 확인
    Server-->>Client: 2. 랜덤 챌린지 데이터 전송
    Note left of Client: 개인키로 챌린지 서명
    Client->>Server: 3. 서명된 응답 전송
    Note right of Server: 등록된 공개키로<br/>서명 검증
    Server-->>Client: 4. 검증 성공 → 접속 허용
```

단계별 설명:

1. **접속 요청**: 클라이언트가 서버에 "나 접속할게"라고 요청
2. **챌린지 전송**: 서버가 랜덤 데이터를 보냄 (매번 다른 값)
3. **서명 응답**: 클라이언트가 **개인키**로 챌린지에 서명하여 전송
4. **검증 및 허용**: 서버가 미리 등록된 **공개키**로 서명을 검증 → 일치하면 인증 성공

> 이 과정에서 **개인키는 절대로 네트워크를 통해 전송되지 않습니다**. 이것이 비밀번호 인증보다 안전한 핵심 이유입니다.

---

### 왜 SSH 키 인증이 비밀번호보다 안전한가

| 비교 항목 | 비밀번호 인증 | SSH 키 인증 |
|-----------|-------------|-------------|
| **유출 위험** | 네트워크에 비밀번호가 전송됨 | 개인키는 절대 전송되지 않음 |
| **브루트포스 공격** | 짧은 비밀번호는 뚫릴 수 있음 | 키 길이가 매우 길어 사실상 불가능 |
| **키 길이** | 보통 8~20자 | RSA 4096비트, Ed25519 256비트 |
| **피싱 위험** | 가짜 사이트에 비밀번호 입력 가능 | 키가 자동으로 동작하므로 피싱 불가 |
| **재사용 위험** | 여러 사이트에 같은 비밀번호 사용 | 서비스별 독립적인 키 생성 가능 |

---

## 6. SSH 키 생성과 등록

### RSA vs Ed25519

| 구분 | RSA | Ed25519 |
|------|-----|---------|
| **등장 시기** | 1977년 | 2011년 |
| **키 길이** | 2048 / 4096 비트 | 256 비트 (고정) |
| **보안성** | 4096비트 시 매우 높음 | 256비트로도 매우 높음 |
| **속도** | 상대적으로 느림 | 빠름 |
| **서명 크기** | 큼 | 작음 (64바이트) |
| **호환성** | 거의 모든 시스템 지원 | 최신 시스템 대부분 지원 |
| **추천** | 레거시 시스템 호환 필요 시 | **기본 추천** |

> **핵심 포인트:** 특별한 이유가 없다면 **Ed25519**를 사용하세요. 더 빠르고, 더 안전하며, 키 길이가 짧아 관리도 편합니다.

---

### SSH 키 생성

#### Ed25519 키 생성 (추천)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### RSA 키 생성 (호환성 필요 시)

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

#### 대화형 프롬프트 설명

```text
$ ssh-keygen -t ed25519 -C "hong@example.com"

Generating public/private ed25519 key pair.

Enter file in which to save the key (/home/user/.ssh/id_ed25519):
→ 저장 경로. 기본값 그대로 Enter (여러 키 사용 시 경로 변경)

Enter passphrase (empty for no passphrase):
→ 키에 대한 추가 비밀번호. 보안을 위해 설정 권장

Enter same passphrase again:
→ passphrase 재입력

Your identification has been saved in /home/user/.ssh/id_ed25519
Your public key has been saved in /home/user/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx hong@example.com
```

---

### SSH 키 구조

키 생성 후 `~/.ssh/` 디렉토리에 파일이 생성됩니다:

```text
~/.ssh/
├── id_ed25519          # 개인키 (절대 공유 금지!)
├── id_ed25519.pub      # 공개키 (GitHub에 등록)
├── known_hosts         # 접속했던 서버의 공개키 목록
└── config              # SSH 설정 파일 (선택)
```

| 파일 | 역할 | 공유 가능? |
|------|------|-----------|
| `id_ed25519` | 개인키 — 나만 가지고 있어야 함 | **절대 불가** |
| `id_ed25519.pub` | 공개키 — 서버에 등록하는 키 | 공개 가능 |
| `known_hosts` | 이전에 접속한 서버 목록 | 불필요 |
| `config` | SSH 접속 설정 (별칭, 키 지정 등) | 보통 비공개 |

```mermaid
flowchart LR
    GEN["ssh-keygen 실행"] --> PRIV["id_ed25519<br/>(개인키)"]
    GEN --> PUB["id_ed25519.pub<br/>(공개키)"]

    PRIV --> LOCAL["내 컴퓨터에 보관<br/>절대 유출 금지"]
    PUB --> GITHUB["GitHub에 등록<br/>Settings → SSH Keys"]

    style GEN fill:#6c5ce7,stroke:#5f27cd,color:#fff
    style PRIV fill:#e17055,stroke:#d63031,color:#fff
    style PUB fill:#55efc4,stroke:#00b894,color:#2d3436
    style LOCAL fill:#e17055,stroke:#d63031,color:#fff
    style GITHUB fill:#55efc4,stroke:#00b894,color:#2d3436
```

---

### GitHub에 공개키 등록

#### Step 1: 공개키 복사

```bash
# Mac/Linux
cat ~/.ssh/id_ed25519.pub

# Windows (Git Bash)
cat ~/.ssh/id_ed25519.pub

# Windows (PowerShell)
Get-Content ~/.ssh/id_ed25519.pub

# 클립보드에 직접 복사 (Mac)
pbcopy < ~/.ssh/id_ed25519.pub

# 클립보드에 직접 복사 (Windows)
clip < ~/.ssh/id_ed25519.pub
```

출력 예시:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG... hong@example.com
```

#### Step 2: GitHub에 등록

1. GitHub → **Settings** → **SSH and GPG keys**
2. **"New SSH key"** 클릭
3. 설정:
   - **Title**: 키를 식별할 이름 (예: "내 노트북", "회사 PC", "집 데스크톱")
   - **Key type**: Authentication Key
   - **Key**: 복사한 공개키 전체를 붙여넣기
4. **"Add SSH key"** 클릭
5. GitHub 비밀번호 확인

---

### SSH 연결 테스트

```bash
ssh -T git@github.com
```

처음 접속 시 다음 메시지가 나타납니다:

```text
The authenticity of host 'github.com (20.200.245.247)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

`yes`를 입력합니다. 성공하면:

```text
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

이 메시지가 나타나면 SSH 인증이 정상적으로 작동하는 것입니다.

---

### SSH Agent 설정

**SSH Agent**는 개인키를 메모리에 로드하여, 매번 passphrase를 입력하지 않아도 되게 해주는 프로그램입니다.

#### Mac / Linux

```bash
# SSH Agent 시작
eval "$(ssh-agent -s)"
# 출력: Agent pid 12345

# 개인키 등록
ssh-add ~/.ssh/id_ed25519
# passphrase 입력 (설정한 경우)
```

Mac에서 Keychain에 passphrase 저장:

```bash
# Mac 전용: Keychain에 passphrase 저장
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

`~/.ssh/config`에 영구 설정:

```text
Host github.com
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519
```

#### Windows (Git Bash)

```bash
# SSH Agent 시작
eval "$(ssh-agent -s)"

# 개인키 등록
ssh-add ~/.ssh/id_ed25519
```

#### Windows (PowerShell, 관리자 권한)

```powershell
# SSH Agent 서비스 시작 (관리자 PowerShell)
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# 키 등록
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

---

## 7. SSH 키 관리 실전

### 여러 GitHub 계정 사용하기

개인 계정과 회사 계정 등 여러 GitHub 계정을 사용해야 할 때, `~/.ssh/config` 파일로 구분합니다.

#### Step 1: 각 계정용 SSH 키 생성

```bash
# 개인용 키
ssh-keygen -t ed25519 -C "personal@email.com" -f ~/.ssh/id_ed25519_personal

# 회사용 키
ssh-keygen -t ed25519 -C "work@company.com" -f ~/.ssh/id_ed25519_work
```

#### Step 2: SSH Config 설정

`~/.ssh/config` 파일을 생성하거나 편집합니다:

```text
# 개인 GitHub 계정 (기본)
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

# 회사 GitHub 계정
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
```

#### Step 3: 사용 방법

```bash
# 개인 계정으로 클론 (기본 github.com 사용)
git clone git@github.com:personal-user/my-project.git

# 회사 계정으로 클론 (github-work 호스트 사용)
git clone git@github-work:company/project.git
```

#### Step 4: 저장소별 Git 사용자 설정

```bash
# 회사 프로젝트 폴더에서 (--global 없이!)
cd company-project
git config user.name "홍길동"
git config user.email "work@company.com"
```

---

### SSH 키 보안 모범 사례

#### 1. Passphrase 설정

```bash
# 키 생성 시 passphrase를 반드시 설정
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter passphrase: (여기서 비밀번호 입력)
```

- passphrase는 개인키 파일 자체를 암호화합니다
- 개인키 파일이 유출되어도 passphrase 없이는 사용 불가
- SSH Agent를 사용하면 매번 입력하지 않아도 됩니다

#### 2. 개인키 파일 권한 설정

```bash
# 개인키: 소유자만 읽기/쓰기 (필수!)
chmod 600 ~/.ssh/id_ed25519

# 공개키: 소유자 읽기/쓰기, 다른 사용자 읽기
chmod 644 ~/.ssh/id_ed25519.pub

# .ssh 디렉토리: 소유자만 접근
chmod 700 ~/.ssh
```

> SSH는 개인키 파일의 권한이 너무 느슨하면 사용을 **거부**합니다. `chmod 600`은 필수입니다.

#### 3. 키 교체 주기

- 개인 프로젝트: 1~2년마다 교체 권장
- 회사/조직: 보안 정책에 따라 (보통 6개월~1년)
- 키 교체 절차: 새 키 생성 → GitHub에 새 공개키 등록 → 이전 키 삭제

#### 4. 키 분실/유출 시 대응

```bash
# 1. 즉시 GitHub에서 해당 공개키 삭제
#    Settings → SSH and GPG keys → 해당 키 Delete

# 2. 새 SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"

# 3. 새 공개키를 GitHub에 등록

# 4. 로컬의 이전 키 파일 삭제
rm ~/.ssh/id_ed25519_compromised
rm ~/.ssh/id_ed25519_compromised.pub
```

---

### GPG 키와 서명된 커밋 (참고)

GitHub에서 커밋 옆에 **"Verified"** 배지가 보이는 것을 본 적이 있을 것입니다. 이것은 **GPG 키로 서명된 커밋**입니다.

```text
커밋 목록:
  ✅ Verified   abc1234  feat: 새 기능 추가       (홍길동)
  ─────────    def5678  fix: 버그 수정           (홍길동)
```

- **GPG 서명**: "이 커밋은 정말로 내가 작성한 것이다"를 암호학적으로 증명
- **SSH 서명**: Git 2.34+에서 SSH 키로도 커밋 서명 가능
- 이 과정에서는 GPG 서명을 필수로 다루지 않지만, 관심 있다면 GitHub 공식 문서를 참고하세요

---

## 8. 실전: 저장소 연동 워크플로

### HTTPS로 시작하기 (초보자 추천)

```bash
# 1. GitHub에서 저장소 생성 (README 포함)

# 2. HTTPS URL로 클론
git clone https://github.com/username/my-project.git
cd my-project

# 3. 파일 수정 후 커밋
echo "Hello World" > hello.txt
git add hello.txt
git commit -m "hello.txt 추가"

# 4. push (첫 push 시 인증 창이 나타남)
git push origin main

# 5. Credential Manager가 인증 정보를 저장하므로
#    다음 push부터는 자동 인증
```

### SSH로 시작하기 (추천)

```bash
# 사전 준비: SSH 키 생성 및 GitHub 등록 완료 상태

# 1. SSH URL로 클론
git clone git@github.com:username/my-project.git
cd my-project

# 2. 파일 수정 후 커밋
echo "Hello World" > hello.txt
git add hello.txt
git commit -m "hello.txt 추가"

# 3. push (SSH 키로 자동 인증)
git push origin main
```

### HTTPS에서 SSH로 전환하기

이미 HTTPS로 클론한 저장소를 SSH로 변경하는 방법:

```bash
# 현재 원격 저장소 URL 확인
git remote -v
# origin  https://github.com/username/my-project.git (fetch)
# origin  https://github.com/username/my-project.git (push)

# HTTPS → SSH로 변경
git remote set-url origin git@github.com:username/my-project.git

# 변경 확인
git remote -v
# origin  git@github.com:username/my-project.git (fetch)
# origin  git@github.com:username/my-project.git (push)
```

### SSH에서 HTTPS로 전환하기

```bash
# SSH → HTTPS로 변경
git remote set-url origin https://github.com/username/my-project.git
```

---

### 자주 쓰는 원격 저장소 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `git remote -v` | 연결된 원격 저장소 확인 | `git remote -v` |
| `git remote add` | 원격 저장소 추가 | `git remote add origin URL` |
| `git remote set-url` | 원격 저장소 URL 변경 | `git remote set-url origin URL` |
| `git remote remove` | 원격 저장소 연결 해제 | `git remote remove origin` |
| `git push -u` | push + upstream 설정 | `git push -u origin main` |
| `git push` | 로컬 커밋을 원격에 전송 | `git push` |
| `git pull` | 원격 변경사항을 가져와서 병합 | `git pull origin main` |
| `git fetch` | 원격 변경사항을 가져오기만 (병합 안 함) | `git fetch origin` |
| `git clone` | 원격 저장소 전체를 복제 | `git clone URL` |

#### git pull vs git fetch

```mermaid
flowchart LR
    subgraph FETCH ["git fetch (안전)"]
        direction TB
        F1["원격 변경사항<br/>다운로드"] --> F2["로컬에<br/>반영 안 함"]
        F2 --> F3["직접 확인 후<br/>merge 필요"]
    end

    FETCH ~~~ PULL

    subgraph PULL ["git pull (편리)"]
        direction TB
        P1["원격 변경사항<br/>다운로드"] --> P2["자동으로<br/>merge"]
        P2 --> P3["바로<br/>작업 가능"]
    end

    style F1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style F2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style F3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style P1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style P2 fill:#55efc4,stroke:#00b894,color:#2d3436
    style P3 fill:#55efc4,stroke:#00b894,color:#2d3436
```

> **핵심 포인트:** `git pull` = `git fetch` + `git merge`입니다. 안전하게 확인 후 병합하려면 `git fetch` → `git log origin/main` → `git merge`를 사용하세요.

---

## 9. 핵심 정리

### 인증 방식 선택 가이드

```mermaid
flowchart TB
    START["GitHub 인증 방식 선택"] --> Q1{"SSH 키<br/>설정할 수 있나요?"}

    Q1 -->|"예"| Q2{"여러 계정을<br/>사용하나요?"}
    Q1 -->|"아니오<br/>(초보/임시환경)"| HTTPS["HTTPS + PAT<br/>+ Credential Manager"]

    Q2 -->|"예"| MULTI["SSH + config 파일<br/>계정별 키 분리"]
    Q2 -->|"아니오<br/>(단일 계정)"| SSH["SSH + Ed25519<br/>가장 편리한 방식"]

    style START fill:#6c5ce7,stroke:#5f27cd,color:#fff
    style Q1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Q2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style HTTPS fill:#74b9ff,stroke:#0984e3,color:#fff
    style SSH fill:#55efc4,stroke:#00b894,color:#2d3436
    style MULTI fill:#00b894,stroke:#00cec9,color:#fff
```

### 전체 설정 체크리스트

| 순서 | 항목 | 명령어/방법 | 확인 |
|------|------|-------------|------|
| 1 | GitHub 계정 생성 | github.com 가입 | [ ] |
| 2 | Git 사용자 설정 | `git config --global user.name / user.email` | [ ] |
| 3 | SSH 키 생성 | `ssh-keygen -t ed25519 -C "email"` | [ ] |
| 4 | GitHub에 공개키 등록 | Settings → SSH Keys → New SSH key | [ ] |
| 5 | SSH 연결 테스트 | `ssh -T git@github.com` | [ ] |
| 6 | SSH Agent 설정 | `ssh-add ~/.ssh/id_ed25519` | [ ] |
| 7 | 저장소 클론 | `git clone git@github.com:user/repo.git` | [ ] |
| 8 | push/pull 테스트 | `git push origin main` | [ ] |

### 요약 비교

| 구분 | HTTPS + PAT | SSH (Ed25519) |
|------|-------------|---------------|
| **초기 설정** | PAT 생성 (5분) | 키 생성 + 등록 (10분) |
| **일상 사용** | Credential Manager 필요 | 자동 인증 |
| **보안** | 토큰 만료 관리 필요 | 키 파일만 안전하게 보관 |
| **여러 계정** | 복잡함 | config 파일로 간단 관리 |
| **방화벽** | 대부분 통과 | 일부 차단 가능 |
| **추천** | 입문 단계, 임시 환경 | **일상적 개발 환경** |

### 주요 명령어 요약

```bash
# === SSH 키 관련 ===
ssh-keygen -t ed25519 -C "email"     # 키 생성
cat ~/.ssh/id_ed25519.pub            # 공개키 확인
ssh -T git@github.com                # 연결 테스트
ssh-add ~/.ssh/id_ed25519            # Agent에 키 등록

# === 원격 저장소 관련 ===
git clone git@github.com:user/repo.git   # SSH로 클론
git remote -v                            # 원격 저장소 확인
git remote set-url origin NEW_URL        # URL 변경
git push -u origin main                  # 첫 push (upstream 설정)
git pull origin main                     # 원격 변경사항 가져오기

# === 인증 문제 해결 ===
git config --global credential.helper manager   # Credential Manager 설정
ssh -vT git@github.com                          # SSH 디버그 모드
```

> **핵심 포인트:** 이 과정에서는 **SSH (Ed25519) 방식**을 기본으로 사용합니다. 한 번 설정하면 매번 비밀번호를 입력할 필요 없이 편리하게 개발에 집중할 수 있습니다.

---

> **이전 강의:** [개발 환경 셋업 가이드](07_dev_environment_setup.md)
