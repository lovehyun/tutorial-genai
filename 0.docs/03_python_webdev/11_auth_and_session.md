# 인증과 인가: 쿠키, 세션, JWT

> "당신이 누구인지 증명하고, 무엇을 할 수 있는지 결정하는 것" -- 웹 보안의 두 기둥, 인증과 인가를 완전히 이해합니다.

---

## 1. 인증(Authentication) vs 인가(Authorization)

### 두 개념의 핵심 차이

웹 애플리케이션 보안에서 가장 먼저 이해해야 할 두 가지 개념이 있습니다.

- **인증(Authentication)**: "당신은 누구인가?" -- 사용자의 **신원을 확인**하는 과정
- **인가(Authorization)**: "당신은 무엇을 할 수 있는가?" -- 확인된 사용자에게 **권한을 부여**하는 과정

### 건물 출입 비유

이 두 개념을 건물 출입에 비유하면 직관적으로 이해할 수 있습니다.

```
건물 보안 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[인증] 1층 로비에서 신분증을 보여준다 → "김철수 씨, 확인되었습니다"
[인가] 출입증에 적힌 권한을 확인한다 → "3층, 5층 접근 가능 / 서버실 접근 불가"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

| 구분 | 인증 (Authentication) | 인가 (Authorization) |
|------|----------------------|---------------------|
| 질문 | "당신은 누구인가?" | "당신은 무엇을 할 수 있는가?" |
| 비유 | 신분증 확인 | 출입 권한 확인 |
| 시점 | **먼저** 수행 | 인증 **이후** 수행 |
| 실패 시 | 401 Unauthorized | 403 Forbidden |
| 방법 | 아이디/비밀번호, 생체인식, OAuth | 역할 기반(RBAC), 권한 목록 |
| 웹 예시 | 로그인 | 관리자 전용 페이지 접근 |

### 인증과 인가의 흐름

```mermaid
flowchart LR
    U["사용자<br/>요청"]
    AUTH["인증<br/>(Authentication)<br/>누구인가?"]
    AUTHZ["인가<br/>(Authorization)<br/>권한이 있는가?"]
    OK["요청 처리<br/>성공"]
    FAIL1["401<br/>Unauthorized"]
    FAIL2["403<br/>Forbidden"]

    U --> AUTH
    AUTH -->|"인증 성공"| AUTHZ
    AUTH -->|"인증 실패"| FAIL1
    AUTHZ -->|"권한 있음"| OK
    AUTHZ -->|"권한 없음"| FAIL2

    style U fill:#74b9ff,stroke:#0984e3,color:#fff
    style AUTH fill:#e17055,stroke:#d63031,color:#fff
    style AUTHZ fill:#6c5ce7,stroke:#4834d4,color:#fff
    style OK fill:#55efc4,stroke:#00b894,color:#2d3436
    style FAIL1 fill:#fd79a8,stroke:#e84393,color:#fff
    style FAIL2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
```

> **핵심 포인트:** 인증은 "신원 확인", 인가는 "권한 확인"입니다. 두 개념은 항상 함께 동작하며, 인증이 먼저 수행된 후 인가가 이루어집니다. 401은 "누군지 모르겠다", 403은 "누군지는 알지만 권한이 없다"입니다.

---

## 2. 쿠키(Cookie)

### HTTP의 한계: 무상태(Stateless)

HTTP는 **무상태 프로토콜**입니다. 서버는 각 요청을 독립적으로 처리하며, 이전 요청을 기억하지 못합니다. 마치 매번 처음 만나는 것처럼 대화하는 것과 같습니다.

```
무상태 문제
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
요청 1: "로그인합니다" → 서버: "로그인 성공!"
요청 2: "내 정보 보여줘" → 서버: "당신이 누구죠...?"  ← 기억 못함!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

이 문제를 해결하기 위해 등장한 것이 **쿠키**입니다.

### 쿠키의 동작 원리

쿠키는 서버가 브라우저에게 전달하는 **작은 데이터 조각**입니다. 브라우저는 이 쿠키를 저장해두었다가 같은 서버에 요청할 때마다 자동으로 함께 전송합니다.

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버

    B->>S: 1. POST /login (id=hong, pw=1234)
    Note over S: 사용자 확인 성공
    S-->>B: 2. 200 OK + Set-Cookie
    Note over B: 쿠키 저장: user_id=hong
    B->>S: 3. GET /profile + Cookie
    Note over S: 쿠키에서 사용자 식별
    S-->>B: 4. 200 OK (name: 홍길동)
    B->>S: 5. GET /orders + Cookie
    S-->>B: 6. 200 OK (orders 목록)
```

### Set-Cookie / Cookie 헤더

서버와 브라우저는 HTTP 헤더를 통해 쿠키를 주고받습니다.

**서버 -> 브라우저 (응답 헤더)**

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
Set-Cookie: theme=dark; Path=/; Max-Age=86400
```

**브라우저 -> 서버 (요청 헤더)**

```http
GET /api/profile HTTP/1.1
Host: example.com
Cookie: session_id=abc123; theme=dark
```

### 쿠키의 주요 속성

| 속성 | 설명 | 예시 | 보안 중요도 |
|------|------|------|-----------|
| **HttpOnly** | JavaScript에서 접근 불가 (XSS 방어) | `HttpOnly` | 매우 높음 |
| **Secure** | HTTPS에서만 전송 | `Secure` | 높음 |
| **SameSite** | 다른 사이트 요청 시 전송 여부 (CSRF 방어) | `SameSite=Lax` | 높음 |
| **Max-Age** | 쿠키 유효 시간 (초 단위) | `Max-Age=3600` | 중간 |
| **Expires** | 쿠키 만료 날짜 | `Expires=Thu, 01 Jan 2026` | 중간 |
| **Path** | 쿠키가 전송되는 URL 경로 | `Path=/api` | 낮음 |
| **Domain** | 쿠키가 전송되는 도메인 | `Domain=.example.com` | 중간 |

```python
# FastAPI에서 쿠키 설정 예시
from fastapi import FastAPI, Response

app = FastAPI()

@app.post("/login")
def login(response: Response):
    response.set_cookie(
        key="session_id",
        value="abc123",
        httponly=True,      # JS에서 접근 불가
        secure=True,        # HTTPS 전용
        samesite="lax",     # CSRF 방어
        max_age=3600,       # 1시간 유효
    )
    return {"message": "로그인 성공"}
```

### 쿠키의 한계

| 한계 | 설명 |
|------|------|
| 용량 제한 | 쿠키 하나당 약 4KB, 도메인당 약 20개 |
| 보안 취약 | 클라이언트에 저장되므로 조작 가능 |
| XSS 공격 | HttpOnly 미설정 시 JavaScript로 탈취 가능 |
| CSRF 공격 | 자동 전송 특성을 악용한 위조 요청 가능 |
| 매 요청 전송 | 불필요한 데이터도 매번 전송되어 네트워크 부담 |

> **핵심 포인트:** 쿠키는 HTTP의 무상태 한계를 극복하는 가장 기본적인 방법이지만, 보안 속성(HttpOnly, Secure, SameSite)을 반드시 설정해야 합니다. 쿠키에 민감한 정보를 직접 저장하는 것은 위험합니다.

---

## 3. 세션(Session)

### 쿠키의 보안 문제 해결

쿠키에 사용자 정보를 직접 저장하면 위변조 위험이 있습니다. 세션은 이 문제를 해결합니다. 핵심 아이디어는 간단합니다: **민감한 정보는 서버에 저장하고, 클라이언트에는 "열쇠(세션 ID)"만 전달하는 것**입니다.

비유하면, 호텔 체크인과 같습니다. 호텔은 고객 정보를 프론트 데스크(서버)에 보관하고, 고객에게는 룸 카드키(세션 ID)만 발급합니다.

### 세션의 동작 원리

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버
    participant DB as 세션 저장소

    B->>S: 1. POST /login (id, password)
    Note over S: 사용자 인증 확인
    S->>DB: 2. 세션 생성 및 저장
    S-->>B: 3. Set-Cookie: session_id=sid_xyz
    Note over B: 세션 ID만 저장 (사용자 정보 없음)
    B->>S: 4. GET /profile + Cookie
    S->>DB: 5. 세션 ID로 사용자 정보 조회
    DB-->>S: 6. user: hong, role: admin
    S-->>B: 7. 200 OK (name: 홍길동)
```

### 세션 ID와 쿠키의 관계

```
쿠키 기반 인증 vs 세션 기반 인증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[쿠키 기반]  Cookie: user=hong; role=admin; email=hong@test.com
             → 모든 정보가 브라우저에 노출! 위변조 가능!

[세션 기반]  Cookie: session_id=sid_xyz
             → 의미 없는 ID만 전달. 정보는 서버에 안전하게 보관!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 세션 저장소 비교

| 저장소 | 속도 | 서버 재시작 시 | 확장성 | 사용 시나리오 |
|--------|------|--------------|--------|-------------|
| **메모리** | 가장 빠름 | 세션 소멸 | 단일 서버만 | 개발/테스트 |
| **Redis** | 매우 빠름 | 유지 가능 | 다중 서버 공유 | 프로덕션 추천 |
| **데이터베이스** | 느림 | 유지 가능 | 다중 서버 공유 | 영속성 필요 시 |
| **파일 시스템** | 느림 | 유지 가능 | 단일 서버만 | 간단한 서비스 |

### 세션의 장단점

| 장점 | 단점 |
|------|------|
| 민감 정보가 서버에 안전하게 저장 | 서버 메모리/저장소 부담 |
| 세션 ID만 전달하므로 네트워크 부담 적음 | 서버 확장 시 세션 공유 문제 발생 |
| 서버에서 즉시 세션 무효화 가능 | 다중 서버 환경에서 Sticky Session 또는 공유 저장소 필요 |
| 구현이 직관적이고 이해하기 쉬움 | 모바일 앱, 마이크로서비스에서는 비효율적 |

> **핵심 포인트:** 세션은 "정보는 서버에, 열쇠는 클라이언트에" 보관하는 방식입니다. 보안은 강화되지만, 서버가 상태를 유지해야 하므로 확장성에 한계가 있습니다.

---

## 4. 토큰 기반 인증과 JWT

### 왜 토큰인가?

세션 기반 인증은 서버가 상태를 유지해야 합니다. 서비스가 커져서 서버를 여러 대로 늘리면 어떻게 될까요?

```
다중 서버 환경의 세션 문제
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
요청 1 → 서버 A: 로그인 성공, 세션 저장 (session_id=xyz)
요청 2 → 서버 B: session_id=xyz? 그런 세션 없는데요! → 401 에러
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

토큰 기반 인증은 이 문제를 해결합니다. **토큰 자체에 사용자 정보를 담아서** 서버가 별도의 상태를 유지하지 않아도 됩니다(Stateless). 어떤 서버가 요청을 받든 토큰만 검증하면 됩니다.

### JWT란?

**JWT(JSON Web Token)**는 당사자 간에 정보를 JSON 형태로 안전하게 전달하기 위한 표준(RFC 7519)입니다.

### JWT의 구조: Header.Payload.Signature

JWT는 점(`.`)으로 구분된 세 부분으로 구성됩니다.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJob25nIiwiZXhwIjoxNzEzNjAwMDAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
└────────── Header ──────────┘└─────────────── Payload ──────────────┘└────── Signature ──────┘
```

```mermaid
flowchart LR
    JWT["JWT 토큰 구조"]

    subgraph H["Header (헤더)"]
        H1["알고리즘: HS256<br/>타입: JWT"]
    end

    subgraph P["Payload (페이로드)"]
        P1["sub: hong (사용자)<br/>exp: 1713600000 (만료시간)<br/>role: admin (커스텀)"]
    end

    subgraph S["Signature (서명)"]
        S1["HMACSHA256(<br/>  base64(header) + . +<br/>  base64(payload),<br/>  SECRET_KEY<br/>)"]
    end

    JWT --> H
    JWT --> P
    JWT --> S

    style JWT fill:#636e72,stroke:#2d3436,color:#fff
    style H fill:#e17055,stroke:#d63031,color:#fff
    style P fill:#0984e3,stroke:#0652DD,color:#fff
    style S fill:#55efc4,stroke:#00b894,color:#2d3436
    style H1 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style P1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style S1 fill:#a8e6cf,stroke:#00b894,color:#2d3436
```

각 부분을 디코딩하면 다음과 같습니다.

```json
// Header (Base64 디코딩)
{
  "alg": "HS256",    // 서명 알고리즘
  "typ": "JWT"       // 토큰 타입
}

// Payload (Base64 디코딩)
{
  "sub": "hong",         // subject: 사용자 식별자
  "exp": 1713600000,     // expiration: 만료 시간 (Unix timestamp)
  "iat": 1713596400,     // issued at: 발급 시간
  "role": "admin"        // 커스텀 클레임: 역할
}

// Signature
// Header와 Payload를 비밀키로 서명하여 위변조 방지
HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

### JWT 인증 흐름

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant S as 서버
    participant DB as 데이터베이스

    C->>S: 1. POST /login {username, password}
    S->>DB: 2. 사용자 조회 & 비밀번호 검증
    DB-->>S: 3. 사용자 정보 반환
    Note over S: 4. JWT 토큰 생성<br/>(사용자 정보 + 비밀키로 서명)
    S-->>C: 5. {"access_token": "eyJhbG...", "token_type": "bearer"}
    Note over C: 토큰 저장<br/>(localStorage 또는 메모리)
    C->>S: 6. GET /api/me<br/>Authorization: Bearer eyJhbG...
    Note over S: 7. 토큰 검증<br/>- 서명 확인 (위변조 여부)<br/>- 만료 시간 확인<br/>- DB 조회 없이 사용자 식별!
    S-->>C: 8. {"username": "hong", "role": "admin"}
```

### Access Token과 Refresh Token

Access Token만 사용하면 보안과 편의성 사이에서 딜레마가 생깁니다.

```
딜레마
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
만료 시간이 길면 → 토큰 탈취 시 오래 악용됨 (보안 취약)
만료 시간이 짧으면 → 자주 로그인해야 함 (사용자 불편)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

이 딜레마를 **두 종류의 토큰**으로 해결합니다.

| 구분 | Access Token | Refresh Token |
|------|-------------|---------------|
| 용도 | API 요청 인증 | Access Token 재발급 |
| 수명 | 짧음 (15분 ~ 1시간) | 김 (7일 ~ 30일) |
| 저장 | 메모리 또는 localStorage | HttpOnly 쿠키 (안전) |
| 전송 | Authorization 헤더 | 쿠키 또는 별도 엔드포인트 |
| 탈취 시 위험 | 짧은 시간만 유효 | 즉시 무효화 가능 (서버 관리) |

### JWT의 장단점

| 장점 | 단점 |
|------|------|
| 무상태(Stateless): 서버 확장에 유리 | 토큰 크기가 세션 ID보다 큼 |
| DB 조회 없이 사용자 정보 확인 가능 | 발급 후 즉시 무효화 어려움 |
| 다중 서버, 마이크로서비스에 적합 | Payload가 Base64 인코딩이라 내용 노출 가능 |
| 모바일 앱, SPA 등 다양한 클라이언트 지원 | 비밀키 노출 시 모든 토큰 무효화 필요 |

> **핵심 포인트:** JWT는 "서명된 정보 봉투"입니다. 봉투 안의 내용(Payload)은 누구나 볼 수 있지만, 서명 덕분에 내용을 위변조할 수 없습니다. 따라서 Payload에 비밀번호 같은 민감 정보를 넣으면 안 됩니다.

---

## 5. 비밀번호 보안

### 절대 평문 저장 금지

비밀번호 보안의 첫 번째 원칙은 간단합니다: **절대로 비밀번호를 평문(plain text)으로 저장하지 마세요.**

```
최악의 DB 설계 (절대 하면 안 됨!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| id | username | password    |
|----|----------|-------------|
| 1  | hong     | mypassword  |  ← 평문 저장! DB 유출 시 재앙!
| 2  | kim      | 12345678    |  ← 이메일, 은행까지 연쇄 피해!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 해싱(Hashing)

해싱은 **단방향 변환**입니다. 비밀번호를 해시 값으로 변환할 수 있지만, 해시 값에서 원래 비밀번호를 역산할 수 없습니다.

```python
# 해싱은 단방향!
"mypassword" → 해싱 → "$2b$12$LJ3m4ys..." (가능)
"$2b$12$LJ3m4ys..." → ??? → "mypassword" (불가능!)
```

### 솔트(Salt)의 역할

같은 비밀번호는 같은 해시 값을 만듭니다. 이를 악용한 **레인보우 테이블 공격**을 막기 위해 **솔트**를 사용합니다. 솔트란 해싱 전에 비밀번호에 추가하는 **랜덤 문자열**입니다.

```
솔트 없이                        솔트와 함께
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"1234" → hash("1234")           "1234" + "x7k9" → hash("1234x7k9")
"1234" → 같은 해시 값! (위험)    "1234" + "m2p5" → 다른 해시 값! (안전)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### bcrypt로 비밀번호 해싱

bcrypt는 솔트를 자동 생성하고, 의도적으로 느리게 설계된 해싱 알고리즘입니다. 느릴수록 무차별 대입 공격(brute force)에 강합니다.

```python
from passlib.context import CryptContext

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해싱 (회원가입 시)
plain_password = "mypassword"
hashed = pwd_context.hash(plain_password)
# 결과: "$2b$12$LJ3m4ysGJf.kB1Q..." (매번 다른 값)

# 비밀번호 검증 (로그인 시)
is_valid = pwd_context.verify("mypassword", hashed)  # True
is_valid = pwd_context.verify("wrongpass", hashed)    # False
```

| 알고리즘 | 특징 | 추천 여부 |
|---------|------|----------|
| **bcrypt** | 솔트 자동 생성, 속도 조절 가능 | 추천 (가장 보편적) |
| **argon2** | 메모리 하드 함수, 최신 표준 | 강력 추천 (최신 프로젝트) |
| **scrypt** | 메모리 사용량 조절 가능 | 추천 |
| MD5, SHA-1 | 빠름 (보안에 취약) | 사용 금지 |

> **핵심 포인트:** 비밀번호는 반드시 bcrypt 또는 argon2로 해싱하여 저장합니다. "해싱 = 단방향, 암호화 = 양방향"이라는 차이를 기억하세요. 비밀번호에는 복호화가 필요 없으므로 해싱을 사용합니다.

---

## 6. FastAPI JWT 인증 구현

이제 실제로 FastAPI에서 JWT 기반 인증 시스템을 구현해보겠습니다.

### 필요한 패키지

```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
```

| 패키지 | 역할 |
|--------|------|
| `python-jose` | JWT 토큰 생성 및 검증 |
| `passlib[bcrypt]` | 비밀번호 해싱 |
| `python-multipart` | OAuth2 폼 데이터 파싱 |

### 전체 구조 개요

```mermaid
flowchart TB
    subgraph Client["클라이언트"]
        REQ["API 요청"]
    end

    subgraph Server["FastAPI 서버"]
        REG["/register 회원가입"]
        LOGIN["/login 로그인 & 토큰 발급"]
        ME["/me 내 정보 조회"]
        HASH["비밀번호 해싱 유틸"]
        JWT_UTIL["JWT 생성/검증"]
        DEP["get_current_user 의존성"]
        OAUTH["OAuth2PasswordBearer 토큰 추출"]
    end

    subgraph DB["데이터베이스"]
        USERS["users 테이블"]
    end

    REQ --> REG
    REQ --> LOGIN
    REQ --> ME

    REG --> HASH
    HASH --> USERS
    LOGIN --> HASH
    LOGIN --> JWT_UTIL
    ME --> OAUTH
    OAUTH --> DEP
    DEP --> JWT_UTIL
    DEP --> USERS

    style Client fill:#74b9ff,stroke:#0984e3,color:#fff
    style Server fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style DB fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style REG fill:#55efc4,stroke:#00b894,color:#2d3436
    style LOGIN fill:#e17055,stroke:#d63031,color:#fff
    style ME fill:#6c5ce7,stroke:#4834d4,color:#fff
    style HASH fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style JWT_UTIL fill:#fd79a8,stroke:#e84393,color:#fff
    style DEP fill:#636e72,stroke:#2d3436,color:#fff
    style OAUTH fill:#fab1a0,stroke:#e17055,color:#2d3436
    style USERS fill:#f9ca24,stroke:#f39c12,color:#2d3436
    style REQ fill:#0984e3,stroke:#0652DD,color:#fff
```

### Step 1: 비밀번호 해싱 유틸리티

```python
# utils/security.py
from passlib.context import CryptContext

# bcrypt 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)
```

### Step 2: JWT 토큰 생성/검증 함수

```python
# utils/jwt_handler.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

# JWT 설정 (실무에서는 환경 변수로 관리)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT Access Token 생성"""
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """JWT 토큰 디코딩 및 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Step 3: Pydantic 모델 정의

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """회원가입 요청 모델"""
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    """로그인 요청 모델"""
    username: str
    password: str

class UserResponse(BaseModel):
    """사용자 응답 모델 (비밀번호 제외!)"""
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    """토큰 응답 모델"""
    access_token: str
    token_type: str
```

### Step 4: OAuth2PasswordBearer 설정과 get_current_user 의존성

```python
# dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# 토큰을 Authorization 헤더에서 자동 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 가상의 사용자 DB (실무에서는 실제 DB 사용)
fake_users_db = {}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """토큰에서 현재 사용자를 추출하는 의존성 함수"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 사용자 조회
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception

    return user
```

### Step 5: 전체 동작 코드

아래는 회원가입, 로그인, 보호된 엔드포인트를 모두 포함한 전체 코드입니다.

```python
# main.py
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

# ─── 설정 ───────────────────────────────────────
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="JWT 인증 예제")

# ─── 비밀번호 해싱 ───────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ─── JWT 토큰 ────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ─── OAuth2 설정 ─────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ─── Pydantic 모델 ──────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── 임시 사용자 저장소 (실무에서는 DB 사용) ────
users_db: dict = {}

# ─── 의존성: 현재 사용자 추출 ────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# ─── 엔드포인트 ─────────────────────────────────
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    """회원가입"""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다")

    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
    }
    return UserResponse(username=user.username, email=user.email)

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """로그인 (토큰 발급)"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return Token(access_token=access_token, token_type="bearer")

@app.get("/me", response_model=UserResponse)
def read_current_user(current_user: dict = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회 (보호된 엔드포인트)"""
    return UserResponse(username=current_user["username"], email=current_user["email"])
```

### 실행 및 테스트

```bash
# 서버 실행
uvicorn main:app --reload

# 1. 회원가입
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "hong", "email": "hong@example.com", "password": "secure123"}'

# 2. 로그인 (토큰 발급)
curl -X POST http://localhost:8000/login \
  -d "username=hong&password=secure123"
# 응답: {"access_token": "eyJhbG...", "token_type": "bearer"}

# 3. 보호된 엔드포인트 접근
curl http://localhost:8000/me \
  -H "Authorization: Bearer eyJhbG..."
# 응답: {"username": "hong", "email": "hong@example.com"}

# 4. 토큰 없이 접근 시
curl http://localhost:8000/me
# 응답: {"detail": "Not authenticated"} (401 에러)
```

> **핵심 포인트:** FastAPI의 `Depends()` 시스템은 인증 로직을 깔끔하게 분리합니다. `get_current_user`를 한 번 정의하면, 어떤 엔드포인트든 `Depends(get_current_user)`만 추가하면 보호된 엔드포인트가 됩니다.

---

## 7. 쿠키 vs 세션 vs JWT 비교

### 종합 비교 표

| 항목 | 쿠키 | 세션 | JWT |
|------|------|------|-----|
| **상태** | 무상태 | 유상태 (서버 저장) | 무상태 |
| **저장 위치** | 브라우저 | 서버 (메모리/Redis) | 클라이언트 |
| **데이터 크기** | 약 4KB 제한 | 서버 제한 없음 | 제한 없음 (헤더 크기 주의) |
| **확장성** | 좋음 | 어려움 (공유 필요) | 매우 좋음 |
| **보안** | 낮음 | 높음 | 중간 |
| **즉시 무효화** | 가능 (삭제) | 가능 (서버에서 삭제) | 어려움 (만료까지 대기) |
| **서버 부담** | 적음 | 높음 | 적음 |
| **CSRF 취약** | 취약 | 취약 | 안전 (헤더 전송 시) |
| **XSS 취약** | HttpOnly로 방어 | HttpOnly로 방어 | localStorage 사용 시 취약 |
| **모바일 지원** | 제한적 | 가능 | 우수 |

### 사용 시나리오별 추천

| 시나리오 | 추천 방식 | 이유 |
|---------|----------|------|
| 전통적 웹사이트 (SSR) | **세션** | 서버 렌더링과 자연스럽게 통합 |
| SPA (React, Vue) | **JWT** | 무상태, API 중심 아키텍처에 적합 |
| 모바일 앱 | **JWT** | 쿠키 없이 헤더로 토큰 전송 |
| 마이크로서비스 | **JWT** | 서비스 간 인증 정보 공유 용이 |
| 다국어/테마 설정 저장 | **쿠키** | 인증과 무관한 사용자 설정 |
| 높은 보안이 필요한 금융 서비스 | **세션 + Redis** | 즉시 세션 무효화 가능 |

### 방식별 특성 비교

```mermaid
flowchart LR
    subgraph Cookie["쿠키 기반"]
        C1["브라우저에 데이터 저장"] --> C2["매 요청 시 자동 전송"] --> C3["위변조 가능"]
    end

    subgraph Session["세션 기반"]
        S1["서버에 데이터 저장"] --> S2["세션 ID만 전달"] --> S3["서버 확장 시 공유 문제"]
    end

    subgraph JWTBlock["JWT 기반"]
        J1["토큰에 정보 포함"] --> J2["Authorization 헤더 전송"] --> J3["무상태, 확장 용이"]
    end

    style Cookie fill:#fd79a8,stroke:#e84393,color:#fff
    style Session fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style JWTBlock fill:#55efc4,stroke:#00b894,color:#2d3436
    style C1 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style C2 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style C3 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style S1 fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style S2 fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style S3 fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style J1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style J2 fill:#74b9ff,stroke:#0984e3,color:#fff
    style J3 fill:#74b9ff,stroke:#0984e3,color:#fff
```

> **핵심 포인트:** "최고의 방식"은 없습니다. 프로젝트의 요구사항에 따라 적합한 방식을 선택해야 합니다. 현대 웹 개발에서는 JWT가 가장 널리 사용되지만, 즉시 세션 무효화가 필요한 경우에는 세션 기반이 더 적합합니다.

---

## 8. 보안 모범 사례

### HTTPS 필수

인증 관련 통신은 반드시 **HTTPS**로 이루어져야 합니다. HTTP에서는 토큰, 비밀번호가 평문으로 노출됩니다.

```
HTTP  → 엽서 (배달원이 내용을 볼 수 있음)
HTTPS → 밀봉 편지 (당사자만 읽을 수 있음)
```

```python
# FastAPI에서 HTTPS 리다이렉트 미들웨어
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 프로덕션에서는 HTTPS 강제
app.add_middleware(HTTPSRedirectMiddleware)
```

### 토큰 만료 시간 설정

```python
# 적절한 만료 시간 예시
ACCESS_TOKEN_EXPIRE_MINUTES = 30      # Access Token: 30분
REFRESH_TOKEN_EXPIRE_DAYS = 7         # Refresh Token: 7일

# 민감한 작업에는 더 짧은 토큰 사용
SENSITIVE_TOKEN_EXPIRE_MINUTES = 5    # 결제, 비밀번호 변경 등: 5분
```

### Refresh Token 전략

```python
# Refresh Token을 이용한 Access Token 재발급
@app.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    """만료된 Access Token을 Refresh Token으로 재발급"""
    payload = decode_access_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 Refresh Token입니다",
        )

    # 새 Access Token 발급
    new_access_token = create_access_token(
        data={"sub": payload["sub"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=new_access_token, token_type="bearer")
```

### CORS 설정

브라우저의 Same-Origin Policy를 관리하기 위해 CORS를 적절히 설정해야 합니다.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-frontend.com"],  # 허용할 도메인 (프로덕션)
    # allow_origins=["*"],                      # 개발 환경에서만 사용!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

무차별 로그인 시도를 방지하기 위해 요청 횟수를 제한합니다.

```python
# slowapi를 사용한 Rate Limiting 예시
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 분당 5회로 제한
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # 로그인 로직...
    pass
```

### 보안 체크리스트

```
인증/인가 보안 체크리스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] HTTPS 적용 (인증서 설정)
[ ] 비밀번호 bcrypt/argon2 해싱
[ ] JWT 비밀키를 환경 변수로 관리
[ ] Access Token 만료 시간 30분 이하
[ ] Refresh Token HttpOnly 쿠키 저장
[ ] CORS 허용 도메인 명시적 지정
[ ] 로그인 Rate Limiting 적용
[ ] SQL Injection 방지 (ORM 사용)
[ ] 에러 메시지에 민감 정보 미포함
[ ] 비밀번호 최소 길이/복잡도 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **핵심 포인트:** 보안은 하나의 기술이 아니라 여러 계층의 방어입니다. HTTPS, 비밀번호 해싱, 토큰 만료, CORS, Rate Limiting 등을 조합하여 다층 방어(Defense in Depth) 전략을 구성해야 합니다.

---

## 9. 핵심 정리

### 인증 방식 비교 요약

```mermaid
flowchart LR
    subgraph Evolution["인증 방식의 발전"]
        direction TB
        CK["쿠키<br/>클라이언트 저장"]
        SS["세션<br/>서버 저장"]
        TK["JWT 토큰<br/>자체 포함"]
    end

    CK -->|"보안 강화"| SS
    SS -->|"확장성 개선"| TK

    style Evolution fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style CK fill:#fd79a8,stroke:#e84393,color:#fff
    style SS fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style TK fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 요약 표

| 항목 | 핵심 내용 |
|------|----------|
| 인증 vs 인가 | 인증 = "누구인가?", 인가 = "무엇을 할 수 있는가?" |
| 쿠키 | 브라우저에 저장되는 작은 데이터, HttpOnly/Secure 필수 |
| 세션 | 서버에 정보 저장, 클라이언트에는 세션 ID만 전달 |
| JWT | 토큰 자체에 정보 포함, 서명으로 위변조 방지, 무상태 |
| JWT 구조 | Header(알고리즘) + Payload(정보) + Signature(서명) |
| 비밀번호 | 반드시 bcrypt/argon2로 해싱, 절대 평문 저장 금지 |
| FastAPI 구현 | OAuth2PasswordBearer + Depends(get_current_user) 패턴 |
| 보안 | HTTPS, 토큰 만료, CORS, Rate Limiting 다층 방어 |

```
오늘 배운 내용 한 줄 요약
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 인증 = 신원 확인 (401), 인가 = 권한 확인 (403)
2. 쿠키: 간단하지만 보안에 취약, 반드시 HttpOnly/Secure 설정
3. 세션: 서버에 저장하여 안전, 하지만 확장성에 한계
4. JWT: 무상태로 확장에 유리, 현대 웹의 표준 인증 방식
5. 비밀번호: bcrypt 해싱 필수, 평문 저장은 절대 금지
6. FastAPI: Depends() 의존성 주입으로 깔끔한 인증 구현
7. 보안: 하나의 기술이 아닌 다층 방어 전략이 핵심
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 다음 강의 미리보기

> 다음 강의 **[12. 파일 처리와 로깅](12_file_io_and_logging.md)**에서는 파일 업로드/다운로드 처리와 애플리케이션 로깅을 학습합니다.
> 오늘 배운 인증 시스템 위에 파일 업로드 기능을 추가하고, 로그인 시도, 접근 기록 등을 로깅하는 방법을 실습합니다.

```python
# 다음 시간 미리보기: 파일 업로드 + 인증
@app.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: dict = Depends(get_current_user),  # 인증된 사용자만!
):
    # 파일 저장 로직
    logger.info(f"사용자 {current_user['username']}이(가) 파일을 업로드했습니다: {file.filename}")
    return {"filename": file.filename, "uploaded_by": current_user["username"]}
```

---

[이전 강의: 10. 게시판 프로젝트](10_board_project.md) | [다음 강의: 12. 파일 처리와 로깅](12_file_io_and_logging.md)
