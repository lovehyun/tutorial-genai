# HTTP 프로토콜 심화

> 웹의 모든 통신은 HTTP라는 약속 위에서 이루어진다

---

## 1. 프로토콜이란?

### 통신 규약 = 대화의 규칙

**프로토콜(Protocol)**이란 두 시스템이 데이터를 주고받기 위해 미리 정해놓은 **규칙**이다.

일상 비유로 이해하면 쉽다.

```
전화 통화의 프로토콜
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 발신자: 전화를 건다 (연결 요청)
2. 수신자: "여보세요" (연결 수락)
3. 대화를 주고받는다 (데이터 전송)
4. "끊을게요" → "네, 안녕히" (연결 종료)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

인터넷에서도 마찬가지다. 컴퓨터끼리 대화하려면 **"어떤 순서로, 어떤 형식으로, 무엇을 보낼지"** 미리 정해야 한다. 그것이 바로 프로토콜이다.

### 인터넷 프로토콜 스택 (TCP/IP 4계층)

```mermaid
flowchart TB
    subgraph Layer4["응용 계층 (Application)"]
        HTTP["HTTP/HTTPS"]
        FTP["FTP"]
        SMTP["SMTP (이메일)"]
        DNS["DNS"]
    end

    subgraph Layer3["전송 계층 (Transport)"]
        TCP["TCP (신뢰성 보장)"]
        UDP["UDP (빠른 전송)"]
    end

    subgraph Layer2["인터넷 계층 (Internet)"]
        IP["IP (주소 지정, 라우팅)"]
    end

    subgraph Layer1["네트워크 접근 계층 (Network Access)"]
        ETH["이더넷 / Wi-Fi"]
    end

    Layer4 --> Layer3 --> Layer2 --> Layer1

    style Layer4 fill:#74b9ff,stroke:#0984e3,color:#fff
    style Layer3 fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style Layer2 fill:#fd79a8,stroke:#e84393,color:#fff
    style Layer1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style HTTP fill:#0984e3,stroke:#0652DD,color:#fff
    style TCP fill:#6c5ce7,stroke:#4834d4,color:#fff
    style IP fill:#e84393,stroke:#c44569,color:#fff
    style ETH fill:#f39c12,stroke:#e67e22,color:#2d3436
    style FTP fill:#0984e3,stroke:#0652DD,color:#fff
    style SMTP fill:#0984e3,stroke:#0652DD,color:#fff
    style DNS fill:#0984e3,stroke:#0652DD,color:#fff
    style UDP fill:#6c5ce7,stroke:#4834d4,color:#fff
```

| 계층 | 역할 | 비유 |
|------|------|------|
| 응용 계층 | 사용자와 가까운 서비스 (웹, 이메일) | 편지 내용 |
| 전송 계층 | 데이터 분할, 순서 보장 | 편지를 봉투에 넣기 |
| 인터넷 계층 | 주소 지정, 경로 결정 | 우편번호 / 배송 경로 |
| 네트워크 접근 | 실제 전기 신호 전송 | 우체국 트럭 |

**HTTP는 응용 계층(Application Layer)에서 동작**하며, 웹 브라우저와 웹 서버 사이의 대화 규칙을 정의한다.

---

## 2. URL 구조 분석

### URL의 각 구성 요소

URL(Uniform Resource Locator)은 인터넷에서 자원의 위치를 나타내는 주소다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  https://www.example.com:443/products?category=books&sort=price#reviews │
│  ─┬───   ───────┬───────  ┬  ───┬───  ──────────────┬──────── ───┬──── │
│   │             │         │     │                   │             │     │
│ scheme        host      port   path              query        fragment  │
│(프로토콜)   (호스트)   (포트) (경로)          (쿼리 문자열)   (프래그먼트)│
└─────────────────────────────────────────────────────────────────────────┘
```

### 각 부분 상세 설명

| 구성 요소 | 예시 | 설명 |
|-----------|------|------|
| **scheme** | `https` | 사용할 프로토콜 (http, https, ftp 등) |
| **host** | `www.example.com` | 서버의 도메인 이름 또는 IP 주소 |
| **port** | `443` | 서버의 포트 번호 (http=80, https=443이 기본) |
| **path** | `/products` | 서버 내 자원의 경로 (폴더/파일 구조) |
| **query** | `category=books&sort=price` | 추가 파라미터 (key=value 형태, &로 구분) |
| **fragment** | `reviews` | 페이지 내 특정 위치 (서버에 전송되지 않음) |

### 도메인 이름과 DNS

사람은 `www.google.com` 같은 이름을 기억하지만, 컴퓨터는 `142.250.196.4` 같은 IP 주소로 통신한다.

**DNS(Domain Name System)**가 도메인을 IP로 변환해준다.

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant DNS as DNS 서버
    participant S as 웹 서버<br/>(142.250.196.4)

    B->>DNS: www.google.com의 IP 주소는?
    DNS-->>B: 142.250.196.4 입니다
    B->>S: HTTP 요청 (142.250.196.4)
    S-->>B: HTTP 응답 (웹 페이지)
```

> DNS는 인터넷의 전화번호부다. 이름(도메인)을 번호(IP)로 바꿔준다.

---

## 3. HTTP 요청 (Request) 구조

클라이언트(브라우저)가 서버에게 보내는 메시지를 **HTTP 요청**이라 한다.

### 요청의 3가지 구성 요소

```mermaid
flowchart LR
    subgraph Request["HTTP 요청 메시지"]
        direction TB
        RL["요청 라인 (Request Line)<br/>GET /api/users HTTP/1.1"]
        RH["요청 헤더 (Headers)<br/>Host: example.com<br/>Accept: application/json"]
        RB["요청 본문 (Body)<br/>(POST/PUT 시 데이터 포함)"]
    end

    RL --> RH --> RB

    style Request fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style RL fill:#e17055,stroke:#d63031,color:#fff
    style RH fill:#74b9ff,stroke:#0984e3,color:#fff
    style RB fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 1) 요청 라인 (Request Line)

```
GET /api/users HTTP/1.1
─┬─ ─────┬──── ───┬────
 │       │        │
메서드  경로   HTTP 버전
```

### 2) 요청 헤더 (Headers)

| 헤더 | 역할 | 예시 |
|------|------|------|
| `Host` | 요청 대상 서버 | `Host: www.example.com` |
| `User-Agent` | 클라이언트 정보 | `User-Agent: Chrome/120` |
| `Accept` | 원하는 응답 형식 | `Accept: application/json` |
| `Content-Type` | 보내는 데이터 형식 | `Content-Type: application/json` |
| `Authorization` | 인증 정보 | `Authorization: Bearer eyJhbG...` |
| `Cookie` | 저장된 쿠키 전송 | `Cookie: session_id=abc123` |

### 3) 요청 본문 (Body)

GET 요청에는 보통 본문이 없고, POST/PUT 요청 시 데이터를 담는다.

### 실제 요청 예시 (Raw HTTP)

**GET 요청 (데이터 조회)**

```http
GET /api/users?page=1&limit=10 HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Cookie: session_id=abc123def456
```

**POST 요청 (데이터 생성)**

```http
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 68
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "name": "홍길동",
  "email": "hong@example.com",
  "age": 25
}
```

---

## 4. HTTP 응답 (Response) 구조

서버가 클라이언트에게 돌려보내는 메시지를 **HTTP 응답**이라 한다.

### 응답의 3가지 구성 요소

```mermaid
flowchart LR
    subgraph Response["HTTP 응답 메시지"]
        direction TB
        SL["상태 라인 (Status Line)<br/>HTTP/1.1 200 OK"]
        RH["응답 헤더 (Headers)<br/>Content-Type: application/json<br/>Content-Length: 42"]
        RB["응답 본문 (Body)<br/>name: 홍길동, age: 25"]
    end

    SL --> RH --> RB

    style Response fill:#dfe6e9,stroke:#636e72,color:#2d3436
    style SL fill:#6c5ce7,stroke:#4834d4,color:#fff
    style RH fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style RB fill:#fab1a0,stroke:#e17055,color:#2d3436
```

### 1) 상태 라인 (Status Line)

```
HTTP/1.1 200 OK
───┬──── ─┬─ ─┬
   │      │   │
HTTP버전  │  상태 텍스트
       상태코드
```

### 2) 응답 헤더 (Headers)

| 헤더 | 역할 | 예시 |
|------|------|------|
| `Content-Type` | 응답 데이터 형식 | `application/json` |
| `Content-Length` | 응답 본문 크기(바이트) | `1024` |
| `Set-Cookie` | 쿠키 설정 | `Set-Cookie: session_id=xyz` |
| `Cache-Control` | 캐시 정책 | `max-age=3600` |
| `Location` | 리다이렉트 대상 URL | `https://new-url.com` |

### 실제 응답 예시 (Raw HTTP)

**성공 응답 (200 OK)**

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 89
Date: Mon, 20 Apr 2026 09:30:00 GMT
Server: nginx/1.24

{
  "id": 1,
  "name": "홍길동",
  "email": "hong@example.com",
  "age": 25
}
```

**에러 응답 (404 Not Found)**

```http
HTTP/1.1 404 Not Found
Content-Type: application/json; charset=utf-8
Content-Length: 52

{
  "error": "Not Found",
  "message": "해당 사용자를 찾을 수 없습니다"
}
```

---

## 5. HTTP 메서드 (Methods)

HTTP 메서드는 서버에게 **"무엇을 하고 싶은지"** 알려주는 동사(verb)이다.

### 주요 메서드와 CRUD 매핑

```mermaid
flowchart LR
    subgraph CRUD["데이터 조작 (CRUD)"]
        direction TB
        C["Create<br/>생성"]
        R["Read<br/>조회"]
        U["Update<br/>수정"]
        D["Delete<br/>삭제"]
    end

    subgraph Methods["HTTP 메서드"]
        direction TB
        POST["POST"]
        GET["GET"]
        PUT["PUT / PATCH"]
        DELETE["DELETE"]
    end

    C --> POST
    R --> GET
    U --> PUT
    D --> DELETE

    style C fill:#55efc4,stroke:#00b894,color:#2d3436
    style R fill:#74b9ff,stroke:#0984e3,color:#fff
    style U fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#ff7675,stroke:#d63031,color:#fff
    style POST fill:#00b894,stroke:#00a383,color:#fff
    style GET fill:#0984e3,stroke:#0652DD,color:#fff
    style PUT fill:#f39c12,stroke:#e67e22,color:#fff
    style DELETE fill:#d63031,stroke:#c0392b,color:#fff
```

### 각 메서드 상세

| 메서드 | 용도 | 본문(Body) | 비유 |
|--------|------|-----------|------|
| **GET** | 데이터 조회 (읽기) | 없음 | 도서관에서 책 찾기 |
| **POST** | 데이터 생성 (쓰기) | 있음 | 새 책을 등록하기 |
| **PUT** | 데이터 전체 수정 | 있음 | 책 정보를 통째로 바꾸기 |
| **PATCH** | 데이터 부분 수정 | 있음 | 책 제목만 수정하기 |
| **DELETE** | 데이터 삭제 | 없음/있음 | 책을 폐기하기 |

### 실제 사용 예시

```http
# 1. 전체 사용자 목록 조회
GET /api/users HTTP/1.1

# 2. 새 사용자 생성
POST /api/users HTTP/1.1
Content-Type: application/json

{"name": "홍길동", "email": "hong@example.com"}

# 3. 사용자 정보 전체 수정 (PUT)
PUT /api/users/1 HTTP/1.1
Content-Type: application/json

{"name": "홍길동", "email": "new@example.com", "age": 30}

# 4. 사용자 이메일만 수정 (PATCH)
PATCH /api/users/1 HTTP/1.1
Content-Type: application/json

{"email": "updated@example.com"}

# 5. 사용자 삭제
DELETE /api/users/1 HTTP/1.1
```

### 멱등성(Idempotent) 개념

**멱등성**이란, 같은 요청을 여러 번 보내도 결과가 동일한 성질이다.

| 메서드 | 멱등성 | 설명 |
|--------|--------|------|
| GET | O | 몇 번을 조회해도 데이터가 변하지 않음 |
| PUT | O | 같은 데이터로 수정하면 결과 동일 |
| DELETE | O | 이미 삭제된 것을 또 삭제해도 결과 동일 |
| POST | X | 같은 요청을 보내면 데이터가 계속 생성됨 |
| PATCH | X | 상대적 변경이 가능하여 결과가 달라질 수 있음 |

> 비유: 에어컨을 "25도로 설정" (PUT, 멱등) vs "온도 1도 낮춰" (PATCH, 비멱등)

---

## 6. HTTP 상태 코드

상태 코드는 서버가 요청 처리 결과를 **3자리 숫자**로 알려주는 것이다.

### 상태 코드 분류

```mermaid
flowchart LR
    SC["HTTP 상태 코드"]

    SC --> C1["1xx 정보<br/>요청 수신, 처리 중"]
    SC --> C2["2xx 성공<br/>요청 정상 처리"]
    SC --> C3["3xx 리다이렉션<br/>추가 동작 필요"]
    SC --> C4["4xx 클라이언트 오류<br/>요청에 문제"]
    SC --> C5["5xx 서버 오류<br/>서버에 문제"]

    style SC fill:#636e72,stroke:#2d3436,color:#fff
    style C1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style C2 fill:#55efc4,stroke:#00b894,color:#2d3436
    style C3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style C4 fill:#fd79a8,stroke:#e84393,color:#fff
    style C5 fill:#ff7675,stroke:#d63031,color:#fff
```

### 상세 상태 코드

#### 1xx: 정보 (Informational)

| 코드 | 의미 | 설명 |
|------|------|------|
| 100 | Continue | 계속 요청해도 됨 |
| 101 | Switching Protocols | WebSocket 등으로 프로토콜 전환 |

#### 2xx: 성공 (Success)

| 코드 | 의미 | 설명 |
|------|------|------|
| **200** | OK | 요청 성공 (가장 흔한 응답) |
| **201** | Created | 새 리소스 생성 완료 (POST 성공) |
| 204 | No Content | 성공했지만 응답 본문 없음 (DELETE 성공) |

#### 3xx: 리다이렉션 (Redirection)

| 코드 | 의미 | 설명 |
|------|------|------|
| **301** | Moved Permanently | 영구적으로 주소 변경 (북마크 업데이트) |
| 302 | Found | 임시 이동 (원래 주소 유지) |
| **304** | Not Modified | 캐시된 내용 그대로 사용해도 됨 |

#### 4xx: 클라이언트 오류 (Client Error)

| 코드 | 의미 | 비유 |
|------|------|------|
| **400** | Bad Request | 잘못된 요청 (편지 주소를 이상하게 씀) |
| **401** | Unauthorized | 인증 안 됨 (신분증 안 가져옴) |
| **403** | Forbidden | 권한 없음 (신분증은 있지만 출입 불가) |
| **404** | Not Found | 리소스 없음 (그 주소에 아무것도 없음) |
| 405 | Method Not Allowed | 허용 안 된 메서드 (읽기 전용인데 수정 시도) |
| **429** | Too Many Requests | 요청 과다 (너무 자주 전화해서 차단) |

#### 5xx: 서버 오류 (Server Error)

| 코드 | 의미 | 비유 |
|------|------|------|
| **500** | Internal Server Error | 서버 내부 오류 (식당 주방에서 사고) |
| 502 | Bad Gateway | 게이트웨이 오류 (중간 배달원이 실수) |
| **503** | Service Unavailable | 서비스 불가 (식당 문 닫음, 점검 중) |

### 자주 만나는 상태 코드 TOP 10

```
실생활 비유로 외우기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
200 OK          → 주문한 음식이 잘 나왔어요
201 Created     → 새 계좌가 개설되었어요
301 Moved       → 가게가 이사했어요 (새 주소 알려줌)
304 Not Modified→ 어제 본 메뉴 그대로예요 (다시 안 줘도 됨)
400 Bad Request → 주문서 내용이 이상해요
401 Unauthorized→ 회원카드를 안 보여줬어요
403 Forbidden   → 회원이긴 한데 VIP 전용이에요
404 Not Found   → 그런 메뉴 없어요
429 Too Many    → 주문 너무 많이 하셔서 잠깐 쉬세요
500 Server Error→ 주방에서 불이 났어요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. HTTP 헤더 상세

헤더는 요청/응답에 대한 **부가 정보(메타데이터)**를 담는 부분이다.

### 주요 요청 헤더

#### Content-Type (콘텐츠 형식)

서버에게 "내가 보내는 데이터 형식이 이것이다"라고 알려준다.

| Content-Type | 용도 | 예시 |
|-------------|------|------|
| `application/json` | JSON 데이터 전송 | API 호출 시 가장 많이 사용 |
| `application/x-www-form-urlencoded` | HTML 폼 데이터 | 로그인 폼 제출 |
| `multipart/form-data` | 파일 업로드 포함 | 이미지/문서 업로드 |
| `text/html` | HTML 문서 | 웹 페이지 |
| `text/plain` | 일반 텍스트 | 단순 문자열 |

#### Authorization (인증)

서버에게 "나는 인증된 사용자다"라고 증명한다.

```http
# Bearer 토큰 방식 (가장 일반적)
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123

# Basic 인증 (ID:PW를 Base64 인코딩)
Authorization: Basic aG9uZzpwYXNzd29yZA==
```

#### Accept (원하는 응답 형식)

서버에게 "이 형식으로 응답해줘"라고 요청한다.

```http
Accept: application/json       # JSON으로 주세요
Accept: text/html              # HTML로 주세요
Accept: */*                    # 아무거나 다 괜찮아요
```

#### Cookie (쿠키 전송)

브라우저에 저장된 쿠키를 서버에게 보낸다.

```http
Cookie: session_id=abc123; theme=dark; lang=ko
```

### 주요 응답 헤더

#### Set-Cookie (쿠키 설정)

서버가 브라우저에게 "이 쿠키를 저장해라"고 지시한다.

```http
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure; Max-Age=3600
```

| 속성 | 의미 |
|------|------|
| `Path=/` | 모든 경로에서 쿠키 전송 |
| `HttpOnly` | JavaScript에서 접근 불가 (보안) |
| `Secure` | HTTPS에서만 전송 |
| `Max-Age=3600` | 1시간 후 만료 |

#### Cache-Control (캐시 정책)

브라우저에게 "이 응답을 얼마나 저장해도 되는지" 알려준다.

```http
Cache-Control: max-age=3600        # 1시간 동안 캐시 사용
Cache-Control: no-cache            # 매번 서버에 확인
Cache-Control: no-store            # 절대 저장하지 마세요
```

#### CORS 헤더 (교차 출처 리소스 공유)

다른 도메인에서의 요청을 허용할지 결정한다.

```http
Access-Control-Allow-Origin: https://my-frontend.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

> CORS는 보안을 위한 브라우저 정책이다. 서버가 "이 출처에서 오는 요청은 허용한다"고 명시해야 한다.

---

## 8. HTTPS와 보안

### HTTP vs HTTPS 차이

```
HTTP  = 엽서 (누구나 내용을 볼 수 있음)
HTTPS = 밀봉 편지 (암호화되어 당사자만 읽을 수 있음)
```

| 구분 | HTTP | HTTPS |
|------|------|-------|
| 포트 | 80 | 443 |
| 암호화 | 없음 | SSL/TLS 암호화 |
| 보안 | 도청/변조 가능 | 안전한 통신 |
| 주소창 | "주의 요함" 경고 | 자물쇠 아이콘 |
| SEO | 불이익 | 구글 검색 우대 |

### SSL/TLS란?

**SSL(Secure Sockets Layer)** / **TLS(Transport Layer Security)**는 데이터를 암호화하여 안전하게 전송하는 기술이다.

- SSL은 과거 명칭, 현재는 TLS를 사용 (TLS 1.2, TLS 1.3)
- HTTPS = HTTP + TLS

### HTTPS 연결 과정 (TLS Handshake 간소화)

```mermaid
sequenceDiagram
    participant C as 클라이언트<br/>(브라우저)
    participant S as 서버

    Note over C,S: TLS Handshake 시작
    C->>S: 1. ClientHello<br/>(지원하는 암호화 목록 전송)
    S-->>C: 2. ServerHello + 인증서<br/>(암호화 방식 선택 + SSL 인증서)
    Note over C: 3. 인증서 검증<br/>(신뢰할 수 있는 서버인지 확인)
    C->>S: 4. 대칭키 교환<br/>(암호화된 세션 키 전송)
    S-->>C: 5. 연결 완료<br/>(Finished)
    Note over C,S: 이후 모든 통신은 암호화됨
    C->>S: 6. 암호화된 HTTP 요청
    S-->>C: 7. 암호화된 HTTP 응답
```

### SSL 인증서

SSL 인증서는 **"이 서버가 진짜 그 서버가 맞다"**는 것을 증명하는 디지털 신분증이다.

- 인증 기관(CA: Certificate Authority)이 발급
- 무료 인증서: Let's Encrypt
- 유료 인증서: DigiCert, GlobalSign 등

### 왜 HTTPS가 필수인지

1. **보안**: 비밀번호, 카드 정보 등이 암호화됨
2. **SEO**: 구글이 HTTPS 사이트를 검색 순위에서 우대
3. **신뢰**: 브라우저가 HTTP 사이트에 "안전하지 않음" 경고 표시
4. **기능**: 최신 웹 API(카메라, 위치 등)는 HTTPS에서만 동작

---

## 9. 쿠키, 세션, 토큰

HTTP는 **무상태(Stateless)** 프로토콜이다. 매 요청이 독립적이라 서버는 이전 요청을 기억하지 못한다. 로그인 상태를 유지하려면 별도의 방법이 필요하다.

### 쿠키 (Cookie)

- 서버가 브라우저에게 전달하는 작은 데이터 조각
- 브라우저가 자동으로 매 요청에 포함하여 전송

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버

    B->>S: 1. 로그인 요청<br/>(ID: hong, PW: 1234)
    S-->>B: 2. 로그인 성공<br/>Set-Cookie: user=hong
    Note over B: 쿠키 저장: user=hong
    B->>S: 3. 다음 요청<br/>Cookie: user=hong
    S-->>B: 4. "홍길동님 환영합니다"
```

### 세션 (Session)

- 사용자 정보를 **서버에 저장**하고, 고유한 세션 ID만 쿠키로 전달
- 더 안전하지만 서버 메모리 사용

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버
    participant DB as 세션 저장소

    B->>S: 1. 로그인 요청
    S->>DB: 2. 세션 생성<br/>(session_id: xyz → user: hong)
    S-->>B: 3. Set-Cookie: session_id=xyz
    Note over B: 세션ID만 저장
    B->>S: 4. 다음 요청<br/>Cookie: session_id=xyz
    S->>DB: 5. xyz 세션 조회
    DB-->>S: 6. user: hong 정보 반환
    S-->>B: 7. "홍길동님 환영합니다"
```

### 토큰 (JWT - JSON Web Token)

- 사용자 정보를 **토큰 자체에 포함** (서버 저장 불필요)
- 토큰 = Header + Payload + Signature

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버

    B->>S: 1. 로그인 요청
    Note over S: JWT 토큰 생성<br/>(사용자 정보 + 서명)
    S-->>B: 2. 토큰 발급<br/>{"token": "eyJhbG..."}
    Note over B: 토큰을 localStorage에 저장
    B->>S: 3. 다음 요청<br/>Authorization: Bearer eyJhbG...
    Note over S: 토큰 검증 (서명 확인)<br/>서버에 별도 조회 없이 사용자 확인
    S-->>B: 4. "홍길동님 환영합니다"
```

### 비교 표

| 구분 | 쿠키 | 세션 | JWT 토큰 |
|------|------|------|----------|
| **저장 위치** | 브라우저 | 서버 | 브라우저 (localStorage) |
| **서버 부담** | 적음 | 높음 (메모리) | 적음 |
| **보안** | 낮음 (노출 위험) | 높음 | 중간 (토큰 탈취 주의) |
| **확장성** | 좋음 | 서버 간 공유 어려움 | 좋음 (서버 무관) |
| **만료** | Max-Age 설정 | 서버에서 관리 | 토큰 내 exp 클레임 |
| **사용 사례** | 설정 저장 (언어, 테마) | 전통적 웹 로그인 | SPA, 모바일 앱 API |

### JWT 구조 미리보기

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJob25nIiwiZXhwIjoxNzEzNjAwMDAwfQ.abc123signature
└──────────────────┘ └──────────────────────────────────────────┘ └───────────────┘
     Header                        Payload                          Signature
 (암호화 알고리즘)         (사용자 정보, 만료 시간)                (위조 방지 서명)
```

---

## 10. HTTP 버전 역사

### 버전별 발전 과정

```mermaid
timeline
    title HTTP 버전 역사
    1991 : HTTP/0.9
         : GET만 지원
         : HTML만 전송
    1996 : HTTP/1.0
         : 헤더 추가
         : 다양한 파일 지원
         : 매번 연결/종료
    1997 : HTTP/1.1
         : Keep-Alive 연결 유지
         : 파이프라이닝
         : 가장 오래 사용된 버전
    2015 : HTTP/2
         : 멀티플렉싱
         : 헤더 압축
         : 서버 푸시
    2022 : HTTP/3
         : QUIC 프로토콜 - UDP 기반
         : 더 빠른 연결
         : 패킷 손실에 강함
```

### 버전별 상세 비교

#### HTTP/0.9 (1991)

```http
GET /index.html

(응답: HTML 문서만 가능, 헤더 없음)
<html><body>Hello World</body></html>
```

- GET 메서드만 존재
- 헤더 없음, HTML만 전송 가능
- 응답 후 바로 연결 종료

#### HTTP/1.0 (1996)

```http
GET /image.png HTTP/1.0
Host: www.example.com
Accept: image/png

HTTP/1.0 200 OK
Content-Type: image/png
Content-Length: 5000

(이미지 바이너리 데이터)
```

- 헤더 도입 (Content-Type 등)
- 상태 코드 도입
- 이미지, CSS 등 다양한 파일 전송 가능
- **단점**: 매 요청마다 TCP 연결/종료 반복 (느림)

#### HTTP/1.1 (1997) - 가장 오래 사용

```http
GET /page.html HTTP/1.1
Host: www.example.com
Connection: keep-alive
```

- **Keep-Alive**: 하나의 연결로 여러 요청 처리 (연결 재사용)
- **파이프라이닝**: 응답을 기다리지 않고 요청을 연속 전송
- **단점**: Head-of-Line Blocking (앞 요청이 느리면 뒤가 기다림)

#### HTTP/2 (2015)

- **멀티플렉싱**: 하나의 연결에서 여러 요청/응답을 동시에 처리
- **헤더 압축**: 반복되는 헤더를 HPACK으로 압축
- **서버 푸시**: 클라이언트가 요청하기 전에 리소스를 미리 전송
- **바이너리 프로토콜**: 텍스트가 아닌 바이너리로 더 효율적

#### HTTP/3 (2022)

- **QUIC 프로토콜**: TCP 대신 UDP 기반
- **0-RTT 연결**: 이전 연결 정보로 즉시 통신 시작
- **패킷 손실 독립**: 하나의 스트림 문제가 다른 스트림에 영향 없음
- 모바일 환경(네트워크 전환)에 강점

### 연결 방식 비교

```mermaid
flowchart LR
    subgraph HTTP1["HTTP/1.0<br/>매번 새 연결"]
        direction TB
        A1["요청1"] --> B1["응답1"]
        A2["연결 끊기"] --> A3["요청2"]
        A3 --> B2["응답2"]
    end

    subgraph HTTP11["HTTP/1.1<br/>연결 유지 (Keep-Alive)"]
        direction TB
        C1["요청1"] --> D1["응답1"]
        D1 --> C2["요청2"]
        C2 --> D2["응답2"]
    end

    subgraph HTTP2["HTTP/2<br/>멀티플렉싱"]
        direction TB
        E1["요청1 ─────"]
        E2["요청2 ─────"]
        E3["요청3 ─────"]
        E1 --> F1["응답1"]
        E2 --> F2["응답2"]
        E3 --> F3["응답3"]
    end

    style HTTP1 fill:#ff7675,stroke:#d63031,color:#fff
    style HTTP11 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style HTTP2 fill:#55efc4,stroke:#00b894,color:#2d3436
```

---

## 핵심 정리

```
HTTP 프로토콜 핵심 요약
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. HTTP = 웹에서 데이터를 주고받는 통신 규약
2. URL = 인터넷 자원의 주소 (scheme://host:port/path?query#fragment)
3. 요청 = 메서드 + 경로 + 헤더 + 본문
4. 응답 = 상태코드 + 헤더 + 본문
5. 메서드: GET(조회), POST(생성), PUT(수정), DELETE(삭제)
6. 상태코드: 2xx(성공), 4xx(클라이언트 오류), 5xx(서버 오류)
7. HTTPS = HTTP + 암호화 (필수!)
8. 인증: 쿠키 → 세션 → JWT 토큰 (발전 순서)
9. HTTP 버전: 1.1(기본) → 2(빠름) → 3(더 빠름)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 실습 과제

### 과제 1: 브라우저 개발자 도구에서 HTTP 확인

1. 크롬에서 F12 → Network 탭 열기
2. 아무 웹사이트 접속
3. 요청/응답의 헤더, 상태 코드, 메서드 확인하기

### 과제 2: curl로 HTTP 요청 보내기

```bash
# GET 요청
curl -v https://jsonplaceholder.typicode.com/users/1

# POST 요청
curl -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "테스트", "body": "내용입니다", "userId": 1}'

# 응답 헤더만 보기
curl -I https://www.google.com
```

### 과제 3: 상태 코드 직접 만나보기

```bash
# 200 OK
curl -o /dev/null -s -w "%{http_code}" https://www.google.com

# 404 Not Found
curl -o /dev/null -s -w "%{http_code}" https://www.google.com/없는페이지

# 301 Redirect
curl -o /dev/null -s -w "%{http_code}" http://google.com
```
