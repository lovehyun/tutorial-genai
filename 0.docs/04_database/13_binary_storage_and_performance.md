# 바이너리 저장과 성능 최적화

> 데이터베이스는 텍스트만 다루지 않습니다 — 이미지, 영상, 음성 파일을 어떻게 저장하고, 쿼리를 빠르게 만들며, 늘어나는 데이터를 효율적으로 관리하는지 04_database 섹션의 마지막 강의에서 종합적으로 정리합니다.

---

## 1. 바이너리 데이터와 데이터베이스

### 바이너리 데이터란

컴퓨터가 다루는 데이터는 크게 두 종류로 나눌 수 있습니다. **텍스트 데이터(Text Data)**는 사람이 읽을 수 있는 문자로 구성되어 있으며, 일반적인 SQL 쿼리에서 `VARCHAR`, `TEXT` 타입으로 저장됩니다. 반면 **바이너리 데이터(Binary Data)**는 0과 1의 비트 패턴으로 구성된 원시 데이터로, 사람이 직접 읽기 어렵습니다.

웹 서비스에서 흔히 다루는 바이너리 데이터의 예시는 다음과 같습니다.

| 유형 | 예시 | 특징 |
|------|------|------|
| 이미지 | JPEG, PNG, WebP, GIF | 수십 KB ~ 수십 MB |
| 문서 | PDF, DOCX, XLSX | 수 KB ~ 수백 MB |
| 동영상 | MP4, AVI, MOV | 수십 MB ~ 수 GB |
| 음성 | MP3, WAV, AAC | 수 MB ~ 수십 MB |
| 압축 파일 | ZIP, TAR.GZ | 크기 다양 |
| 모델 가중치 | `.bin`, `.pt`, `.onnx` | 수백 MB ~ 수십 GB |

**실생활 비유:** 텍스트 데이터는 **편지**와 같습니다. 편지는 봉투 안에 바로 넣을 수 있고, 내용을 쉽게 읽고 검색할 수 있습니다. 반면 바이너리 데이터는 **소포**와 같습니다. 소포는 부피가 크고 내용물을 직접 열람하기 어려우며, 보관 방법 자체가 편지와 다릅니다. 편지는 파일 캐비닛에 꽂아두면 되지만, 소포는 창고가 필요합니다.

### 웹 서비스에서 바이너리 데이터 처리의 필요성

현대 웹 서비스는 다양한 형태의 바이너리 데이터를 필수적으로 처리합니다.

- 사용자 프로필 이미지 업로드 및 표시
- 게시글에 첨부된 문서나 이미지
- 생성형 AI 서비스의 입력 이미지 / 출력 결과물 저장
- 음성 인식 서비스의 오디오 파일 수신
- 동영상 스트리밍 플랫폼의 콘텐츠 관리

이러한 데이터를 어디에, 어떻게 저장하느냐는 서비스 성능과 비용에 직접적인 영향을 미칩니다.

### 바이너리 데이터 저장 전략 개요

```mermaid
flowchart TB
    A[바이너리 데이터 수신]
    A --> B{저장 전략 선택}
    B --> C[BLOB 방식\nDB 내부 저장]
    B --> D[파일 경로 방식\n로컬 파일시스템]
    B --> E[클라우드 스토리지\nS3 / GCS / Azure]

    C --> C1[소규모 파일\n수십 KB 이하]
    C --> C2[트랜잭션 일관성\n최우선]
    D --> D1[중소규모 서비스\n단일 서버 운영]
    D --> D2[빠른 파일 접근\n필요]
    E --> E1[대규모 서비스\n다중 서버]
    E --> E2[무제한 확장성\n필요]

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style C fill:#0984e3,stroke:#74b9ff,color:#fff
    style D fill:#0984e3,stroke:#74b9ff,color:#fff
    style E fill:#0984e3,stroke:#74b9ff,color:#fff
    style C1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style C2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style D1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style D2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style E1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style E2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

> **핵심 포인트:** 바이너리 데이터는 텍스트 데이터와 근본적으로 보관 방법이 다릅니다. 파일의 크기, 서비스 규모, 트랜잭션 일관성 요구 수준에 따라 BLOB, 파일 경로, 클라우드 스토리지 중 적절한 전략을 선택해야 합니다.

---

## 2. BLOB 저장 방식

### BLOB이란

**BLOB(Binary Large Object)**은 데이터베이스 안에 바이너리 데이터를 직접 저장하는 방식입니다. SQLite는 `BLOB` 타입을 기본 지원하며, MySQL은 `BLOB` / `MEDIUMBLOB` / `LONGBLOB`, PostgreSQL은 `BYTEA` 타입을 제공합니다.

| DB 종류 | 타입명 | 최대 크기 |
|---------|--------|-----------|
| SQLite | BLOB | 이론상 무제한 (실용적으로 수 GB) |
| MySQL | TINYBLOB | 255 bytes |
| MySQL | BLOB | 65 KB |
| MySQL | MEDIUMBLOB | 16 MB |
| MySQL | LONGBLOB | 4 GB |
| PostgreSQL | BYTEA | 1 GB |

### 이미지를 BLOB으로 저장하는 코드 예제

```python
# blob_storage.py -- BLOB으로 이미지 저장
import sqlite3

def save_image_as_blob(db_path, image_path):
    """이미지 파일을 BLOB으로 DB에 저장"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            data BLOB NOT NULL,
            file_size INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    with open(image_path, 'rb') as f:
        image_data = f.read()

    cursor.execute(
        "INSERT INTO images (filename, content_type, data, file_size) VALUES (?, ?, ?, ?)",
        ("photo.jpg", "image/jpeg", image_data, len(image_data))
    )
    conn.commit()
    conn.close()

def load_image_from_blob(db_path, image_id):
    """BLOB에서 이미지를 읽어 파일로 저장"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT filename, data FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()

    if row:
        filename, data = row
        with open(f"restored_{filename}", 'wb') as f:
            f.write(data)

    conn.close()
```

Python에서 SQLite BLOB 저장 시 `bytes` 객체를 그대로 바인딩하면 됩니다. SQLite3 드라이버가 자동으로 BLOB 타입으로 처리합니다.

### BLOB 방식의 장단점

| 항목 | 내용 |
|------|------|
| **장점** | 데이터와 파일이 한 곳에 저장되어 백업이 단순함 |
| **장점** | 트랜잭션으로 파일과 메타데이터의 일관성 보장 |
| **장점** | 파일시스템 권한 관리 불필요 |
| **장점** | 파일 유실 위험 없음 |
| **단점** | DB 파일 크기가 급격히 증가함 |
| **단점** | DB 백업/복원 시간이 오래 걸림 |
| **단점** | 대용량 파일 조회 시 메모리 부담 |
| **단점** | CDN, 정적 파일 서버 등과 연동 어려움 |
| **단점** | SELECT 쿼리에서 불필요하게 큰 데이터 전송 가능 |

> **핵심 포인트:** BLOB 방식은 소규모 서비스에서 단순성을 극대화할 때 적합합니다. 파일 크기가 1 MB를 초과하거나 파일 수가 수천 개를 넘는다면 다른 방식을 검토해야 합니다.

---

## 3. 파일 경로 저장 방식

### 경로(URL)만 DB에 저장하는 구조

파일 경로 방식은 실제 바이너리 파일을 파일시스템(또는 클라우드)에 저장하고, 데이터베이스에는 그 **경로 문자열만** 저장하는 방법입니다.

**실생활 비유:** 도서관에서 책을 어디에 보관하는지 상상해 보십시오. 책 자체를 카드 목록함에 넣는 것이 BLOB 방식이라면, 파일 경로 방식은 카드 목록함에는 책의 위치(서가 번호, 열, 단)만 적고, 실제 책은 서가에 보관하는 것입니다. 사서는 카드만 보고 책을 찾을 수 있습니다.

### 디렉토리 구조 설계

파일이 많아질수록 체계적인 디렉토리 구조가 필요합니다. 대표적인 전략은 두 가지입니다.

**날짜 기반 구조:**
```
uploads/
  2024/
    01/
      15/
        abc123.jpg
        def456.pdf
    02/
      ...
```

**해시 기반 구조:**
```
uploads/
  a3/
    f7/
      a3f7b2c9d1e4...jpg   ← 파일 MD5/SHA256 앞 4자리를 디렉토리로
```

### 파일 업로드와 경로 저장 코드 예제

```python
# filepath_storage.py -- 파일 경로 저장 방식
import sqlite3
import os
import uuid
import shutil
from datetime import datetime

UPLOAD_DIR = "uploads"

def save_file_with_path(db_path, file_path):
    """파일을 uploads 디렉토리에 저장하고 경로를 DB에 기록"""
    # ── 저장 경로 생성 (날짜별 디렉토리) ──
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(UPLOAD_DIR, date_dir)
    os.makedirs(save_dir, exist_ok=True)

    # ── 고유 파일명 생성 ──
    ext = os.path.splitext(file_path)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(save_dir, unique_name)

    # ── 파일 복사 ──
    shutil.copy2(file_path, save_path)

    # ── DB에 경로 저장 ──
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            content_type TEXT,
            file_size INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    file_size = os.path.getsize(save_path)
    cursor.execute(
        "INSERT INTO files (original_name, stored_path, content_type, file_size) VALUES (?, ?, ?, ?)",
        (os.path.basename(file_path), save_path, "image/jpeg", file_size)
    )
    conn.commit()
    conn.close()

def get_file_path(db_path, file_id):
    """DB에서 파일 경로를 조회하여 반환"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT stored_path FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
```

### 파일 경로 방식의 장단점

| 항목 | 내용 |
|------|------|
| **장점** | DB 파일 크기를 작게 유지 가능 |
| **장점** | 파일 서버 / CDN 연동이 용이함 |
| **장점** | 대용량 파일도 스트리밍으로 서빙 가능 |
| **장점** | DB 백업과 파일 백업을 분리하여 관리 유연 |
| **단점** | DB와 파일이 분리되어 일관성 유지가 어려움 |
| **단점** | 파일 삭제 시 DB 레코드와 동기화 필요 |
| **단점** | 파일 유실(경로는 있으나 파일 없음) 위험 |
| **단점** | 서버 이전 시 파일과 DB를 함께 이동해야 함 |

### BLOB vs 파일 경로 종합 비교

| 비교 항목 | BLOB 방식 | 파일 경로 방식 |
|-----------|-----------|----------------|
| 저장 위치 | DB 내부 | 파일시스템 / 클라우드 |
| DB 크기 영향 | 매우 큼 | 거의 없음 |
| 백업 단순성 | 매우 단순 | DB + 파일 별도 백업 |
| 트랜잭션 일관성 | 완벽 보장 | 수동 관리 필요 |
| CDN 연동 | 불가 | 용이 |
| 적합한 파일 크기 | 수 KB 이하 | 제한 없음 |
| 적합한 서비스 규모 | 소규모 | 중대규모 |
| 파일 유실 위험 | 없음 | 있음 |

### BLOB vs 파일 경로 결정 기준 플로우차트

```mermaid
flowchart TB
    S[파일 저장 방식 선택]
    S --> Q1{파일 평균 크기가\n1 MB 초과?}
    Q1 -->|아니오| Q2{동시 사용자가\n100명 초과?}
    Q1 -->|예| Q3{다중 서버\n환경인가?}
    Q2 -->|아니오| BLOB[BLOB 방식 권장]
    Q2 -->|예| FP[파일 경로 방식 권장]
    Q3 -->|예| CLOUD[클라우드 스토리지 권장]
    Q3 -->|아니오| FP2[파일 경로 방식 권장]

    BLOB --> N1[트랜잭션 일관성\n단순 백업 장점]
    FP --> N2[CDN 연동 가능\nDB 경량화]
    FP2 --> N3[로컬 파일시스템\n+경로 저장]
    CLOUD --> N4[S3 / GCS / Azure\n무제한 확장]

    style S fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style Q1 fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style Q2 fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style Q3 fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style BLOB fill:#0984e3,stroke:#74b9ff,color:#fff
    style FP fill:#0984e3,stroke:#74b9ff,color:#fff
    style FP2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style CLOUD fill:#e17055,stroke:#fab1a0,color:#fff
    style N1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style N2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style N3 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style N4 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

> **핵심 포인트:** 파일 경로 방식은 DB와 파일의 분리에서 오는 불일치 위험을 항상 고려해야 합니다. 파일을 먼저 저장한 후 DB에 경로를 기록하고, 실패 시 파일을 삭제하는 롤백 로직이 필요합니다.

---

## 4. 클라우드 스토리지 연동

### 클라우드 스토리지 서비스 개요

클라우드 스토리지는 파일 경로 방식의 **진화된 형태**입니다. 로컬 파일시스템 대신 인터넷 어딘가의 무한에 가까운 저장소에 파일을 보관합니다. 대표적인 서비스는 다음과 같습니다.

| 서비스 | 제공사 | 특징 |
|--------|--------|------|
| Amazon S3 | AWS | 가장 널리 사용, 생태계 풍부 |
| Google Cloud Storage (GCS) | Google | BigQuery 등 GCP 서비스와 연동 용이 |
| Azure Blob Storage | Microsoft | Azure AD 통합 인증 강점 |
| Cloudflare R2 | Cloudflare | S3 호환, 무료 egress 비용 |
| MinIO | 오픈소스 | 자체 호스팅 가능, S3 호환 API |

**실생활 비유:** 파일 경로 방식이 회사 건물 안의 **창고**에 물건을 보관하는 것이라면, 클라우드 스토리지는 전국에 분산된 **물류 창고 네트워크**를 빌려 쓰는 것입니다. 물건이 아무리 많아져도 공간이 부족하지 않고, 전국 어디서든 빠르게 배송(CDN)받을 수 있습니다.

### Presigned URL 개념

클라우드 스토리지에서 중요한 개념 중 하나가 **Presigned URL**입니다. 클라이언트가 서버를 거치지 않고 클라우드 스토리지에 직접 파일을 업로드하거나 다운로드할 수 있는 임시 URL입니다.

- 서버의 부담을 줄이고 대역폭 비용을 절감합니다.
- URL에 만료 시간을 설정하여 보안을 유지합니다.
- 사전 서명(Pre-sign)된 인증 정보가 URL에 포함됩니다.

### 클라우드 스토리지 연동 아키텍처

```mermaid
flowchart TB
    CL["클라이언트"]
    API["API 서버"]
    DB[("데이터베이스")]
    S3[("클라우드 스토리지")]
    CDN["CDN"]

    CL -->|"1. 업로드 요청"| API
    API -->|"2. Presigned URL 발급"| CL
    CL -->|"3. 파일 직접 업로드"| S3
    S3 -->|"4. 업로드 완료 알림"| API
    API -->|"5. 메타데이터 저장"| DB
    CL -->|"6. 파일 요청"| CDN
    CDN -->|"캐시 미스 시 원본 요청"| S3

    style CL fill:#fd79a8,stroke:#e84393,color:#fff
    style API fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style DB fill:#0984e3,stroke:#74b9ff,color:#fff
    style S3 fill:#e17055,stroke:#fab1a0,color:#fff
    style CDN fill:#55efc4,stroke:#00b894,color:#2d3436
```

### boto3(AWS SDK) 코드 맛보기

```python
# s3_storage.py -- AWS S3 파일 업로드 및 Presigned URL 발급
import boto3
from botocore.exceptions import ClientError

def upload_file_to_s3(file_path, bucket_name, object_key):
    """로컬 파일을 S3 버킷에 업로드"""
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        return f"s3://{bucket_name}/{object_key}"
    except ClientError as e:
        print(f"업로드 실패: {e}")
        return None

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    """다운로드용 Presigned URL 생성 (기본 1시간 유효)"""
    s3_client = boto3.client('s3')
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"URL 생성 실패: {e}")
        return None

def generate_presigned_post(bucket_name, object_key, expiration=300):
    """클라이언트가 직접 업로드할 수 있는 Presigned POST 데이터 생성"""
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_key,
            Fields={"Content-Type": "image/jpeg"},
            Conditions=[{"Content-Type": "image/jpeg"}],
            ExpiresIn=expiration
        )
        return response  # {'url': ..., 'fields': {...}}
    except ClientError as e:
        print(f"Presigned POST 생성 실패: {e}")
        return None
```

> **핵심 포인트:** 클라우드 스토리지를 사용할 때 DB에는 S3 경로(`s3://bucket/key`)나 공개 URL만 저장합니다. Presigned URL은 임시로 생성하며 DB에 저장하지 않습니다.

---

## 5. 쿼리 최적화

### 느린 쿼리를 식별하는 방법

쿼리 최적화의 첫 번째 단계는 **느린 쿼리를 찾는 것**입니다. 문제가 있는 쿼리를 특정하지 않고 무작정 코드를 바꾸면 효과가 없습니다.

**실생활 비유:** 도서관에서 특정 책을 찾는다고 가정합니다. 목록 없이 서가를 하나하나 뒤지는 것이 **인덱스 없는 Full Table Scan**이라면, 카드 목록함에서 제목을 찾아 서가 번호를 확인하는 것이 **인덱스를 활용한 검색**입니다. 먼저 어떤 경로로 책을 찾고 있는지 확인하는 것이 `EXPLAIN`의 역할입니다.

### EXPLAIN / EXPLAIN QUERY PLAN

SQLite와 MySQL/PostgreSQL 모두 쿼리 실행 계획을 확인하는 명령어를 제공합니다.

**SQLite:**
```sql
-- 실행 계획 확인 (SCAN = Full Scan, SEARCH = Index 사용)
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE user_id = 42 AND status = 'pending';

-- 예시 출력
-- SCAN TABLE orders          ← 인덱스 없음, 전체 탐색
-- SEARCH TABLE orders USING INDEX idx_user_id  ← 인덱스 사용
```

**MySQL:**
```sql
-- 상세 실행 계획
EXPLAIN SELECT * FROM orders WHERE user_id = 42;

-- type 컬럼이 'ALL'이면 Full Scan (나쁨), 'ref'/'range'면 인덱스 사용 (좋음)
```

**PostgreSQL:**
```sql
-- 실제 실행 통계 포함
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;
```

### 쿼리 최적화 단계별 프로세스

```mermaid
flowchart LR
    START["느린 응답"] --> A["쿼리 로그 + EXPLAIN"]
    A --> C{"Full Scan?"}
    C -->|"예"| D["인덱스 추가"] --> I["재측정"]
    C -->|"아니오"| E{"SELECT * ?"}
    E -->|"예"| G["컬럼 명시"] --> I
    E -->|"아니오"| H{"N+1 문제?"}
    H -->|"예"| J["JOIN/Eager Loading"] --> I
    H -->|"아니오"| K["쿼리 재작성"] --> I
    I --> L{"목표 달성?"}
    L -->|"예"| END["완료"]
    L -->|"아니오"| M["캐싱 추가"] --> END

    style START fill:#e17055,stroke:#fab1a0,color:#fff
    style A fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style C fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style D fill:#0984e3,stroke:#74b9ff,color:#fff
    style E fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style G fill:#0984e3,stroke:#74b9ff,color:#fff
    style H fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style I fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style J fill:#0984e3,stroke:#74b9ff,color:#fff
    style K fill:#0984e3,stroke:#74b9ff,color:#fff
    style L fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style M fill:#fd79a8,stroke:#e84393,color:#fff
    style END fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 쿼리 최적화 핵심 체크리스트

| 항목 | 나쁜 예시 | 좋은 예시 |
|------|-----------|-----------|
| 컬럼 선택 | `SELECT *` | `SELECT id, name, email` |
| 인덱스 활용 | `WHERE YEAR(created_at) = 2024` | `WHERE created_at >= '2024-01-01'` |
| LIKE 검색 | `WHERE name LIKE '%홍%'` | `WHERE name LIKE '홍%'` (앞에만 와일드카드 없이) |
| N+1 문제 | 루프 안에서 건별 SELECT | JOIN 또는 IN절로 일괄 조회 |
| 불필요한 정렬 | `ORDER BY` on uncached col | 인덱스 컬럼으로 정렬 |
| 중복 제거 | `DISTINCT` 남용 | GROUP BY 또는 쿼리 재설계 |

### 느린 쿼리 vs 최적화된 쿼리 코드 예제

```python
# query_optimization.py -- N+1 문제 해결 예시
import sqlite3

# ── 나쁜 예시: N+1 문제 (사용자마다 개별 쿼리 발생) ──
def get_user_orders_bad(db_path, user_ids):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    result = []
    for user_id in user_ids:                          # N번 반복
        cursor.execute(
            "SELECT * FROM orders WHERE user_id = ?",  # 매번 DB 왕복
            (user_id,)
        )
        result.extend(cursor.fetchall())
    conn.close()
    return result

# ── 좋은 예시: IN절로 한 번에 조회 ──
def get_user_orders_good(db_path, user_ids):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ",".join("?" * len(user_ids))       # ?, ?, ?
    cursor.execute(
        f"SELECT id, user_id, total, status FROM orders WHERE user_id IN ({placeholders})",
        user_ids
    )
    result = cursor.fetchall()
    conn.close()
    return result

# ── 좋은 예시: JOIN으로 연관 데이터 한 번에 조회 ──
def get_users_with_orders(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            u.id,
            u.name,
            u.email,
            COUNT(o.id)   AS order_count,
            SUM(o.total)  AS total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name, u.email
    """)
    result = cursor.fetchall()
    conn.close()
    return result
```

> **핵심 포인트:** N+1 문제는 ORM을 사용할 때 특히 자주 발생합니다. Django ORM의 `select_related()` / `prefetch_related()`, SQLAlchemy의 `joinedload()` 등 Eager Loading 기능을 적극 활용해야 합니다.

---

## 6. 데이터베이스 용량 관리

### 데이터 증가에 따른 문제

서비스가 성장할수록 데이터가 쌓이고, 이는 여러 문제를 일으킵니다.

| 문제 유형 | 증상 | 대응책 |
|-----------|------|--------|
| 쿼리 성능 저하 | 응답 시간 증가 | 인덱스, 파티셔닝 |
| 저장 공간 부족 | 디스크 용량 초과 | 아카이빙, 삭제 정책 |
| 백업 시간 증가 | 백업 윈도우 초과 | 증분 백업, 파티셔닝 |
| 메모리 부족 | OOM, 스왑 사용 | 인덱스 최적화, 캐싱 |

### 파티셔닝 개념

**파티셔닝(Partitioning)**은 큰 테이블을 더 작은 물리적 단위로 분할하는 기법입니다.

**수평 파티셔닝(Horizontal Partitioning / Sharding):** 행(Row)을 기준으로 분할합니다. 예를 들어 `orders` 테이블을 연도별로 나누어 `orders_2023`, `orders_2024`, `orders_2025`로 관리합니다.

**수직 파티셔닝(Vertical Partitioning):** 열(Column)을 기준으로 분할합니다. 자주 조회하는 컬럼과 거의 조회하지 않는 대용량 컬럼(예: 본문 TEXT)을 별도 테이블로 분리합니다.

### 데이터 생명주기 관리

```mermaid
flowchart LR
    HOT[핫 데이터\n최근 3개월\n빈번한 읽기/쓰기]
    WARM[웜 데이터\n3개월~1년\n가끔 읽기]
    COLD[콜드 데이터\n1년 이상\n거의 접근 없음]
    ARCHIVE[아카이브\n별도 DB/스토리지\n감사/복원용]
    DELETE[삭제\n법적 보존 기간\n만료 후]

    HOT -->|자동 아카이빙\n스케줄러| WARM
    WARM -->|자동 아카이빙| COLD
    COLD -->|장기 보존| ARCHIVE
    COLD -->|정책에 따라| DELETE

    style HOT fill:#e17055,stroke:#fab1a0,color:#fff
    style WARM fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style COLD fill:#0984e3,stroke:#74b9ff,color:#fff
    style ARCHIVE fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style DELETE fill:#b2bec3,stroke:#dfe6e9,color:#2d3436
```

### VACUUM으로 공간 회수 (SQLite)

SQLite에서 데이터를 `DELETE`해도 실제 디스크 공간이 즉시 반환되지 않습니다. 삭제된 페이지가 "빈 페이지"로 표시만 될 뿐, 파일 크기는 그대로입니다. `VACUUM` 명령으로 실제 공간을 회수합니다.

```sql
-- SQLite: 삭제된 공간 회수 및 DB 파일 최적화
VACUUM;

-- 자동 VACUUM 설정 (삭제 시마다 조금씩 정리)
PRAGMA auto_vacuum = INCREMENTAL;
PRAGMA incremental_vacuum(100);  -- 100 페이지씩 정리
```

### 자동 아카이빙 스크립트 예제

```python
# auto_archiving.py -- 오래된 로그 데이터 자동 아카이빙
import sqlite3
from datetime import datetime, timedelta

def archive_old_logs(main_db, archive_db, days_threshold=90):
    """
    main_db의 logs 테이블에서 days_threshold일 이상 된 레코드를
    archive_db로 이동하고 main_db에서 삭제
    """
    cutoff_date = (datetime.now() - timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    print(f"아카이빙 기준일: {cutoff_date}")

    main_conn = sqlite3.connect(main_db)
    archive_conn = sqlite3.connect(archive_db)

    # ── 아카이브 DB 테이블 생성 (없는 경우) ──
    archive_conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            level TEXT,
            message TEXT,
            created_at TEXT,
            archived_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── 이동 대상 조회 ──
    rows = main_conn.execute(
        "SELECT id, level, message, created_at FROM logs WHERE created_at < ?",
        (cutoff_date,)
    ).fetchall()

    if not rows:
        print("아카이빙 대상 없음")
        main_conn.close()
        archive_conn.close()
        return

    print(f"아카이빙 대상: {len(rows)}건")

    # ── 아카이브 DB에 삽입 ──
    archive_conn.executemany(
        "INSERT OR IGNORE INTO logs (id, level, message, created_at) VALUES (?, ?, ?, ?)",
        rows
    )
    archive_conn.commit()

    # ── 원본 DB에서 삭제 ──
    ids = [row[0] for row in rows]
    placeholders = ",".join("?" * len(ids))
    main_conn.execute(f"DELETE FROM logs WHERE id IN ({placeholders})", ids)
    main_conn.commit()

    # ── SQLite 공간 회수 ──
    main_conn.execute("VACUUM")
    main_conn.commit()

    print(f"아카이빙 완료: {len(rows)}건 이동")
    main_conn.close()
    archive_conn.close()
```

> **핵심 포인트:** 데이터 아카이빙은 서비스 초기부터 정책을 수립해야 합니다. "언제까지 데이터를 보존해야 하는가"는 기술 문제가 아니라 법률, 비즈니스, 운영 정책의 문제입니다. 아카이빙 후에는 반드시 복원 절차도 테스트해야 합니다.

---

## 7. 연결 풀링과 캐싱

### 커넥션 풀(Connection Pool) 개념

데이터베이스 연결(Connection)을 생성하는 것은 비용이 큰 작업입니다. TCP 핸드셰이크, 인증, 세션 초기화 등의 과정이 필요합니다. **커넥션 풀**은 미리 여러 개의 연결을 만들어 놓고 요청이 들어올 때마다 빌려주고 반납받는 방식입니다.

**실생활 비유:** 택시를 매번 공장에서 새로 만들어서 운행하는 것이 아니라, 차고지(풀)에 여러 대의 택시를 대기시켜 놓고 손님이 오면 배차하는 것입니다.

```python
# connection_pool.py -- SQLAlchemy 커넥션 풀 설정 예시
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:password@localhost/mydb",
    pool_size=10,          # 기본 유지할 연결 수
    max_overflow=20,       # 피크 시 추가 허용 연결 수
    pool_timeout=30,       # 연결 대기 최대 시간 (초)
    pool_recycle=3600,     # 1시간마다 연결 재생성 (서버 타임아웃 방지)
    pool_pre_ping=True     # 사용 전 연결 유효성 확인
)
```

### Redis를 활용한 쿼리 캐싱

자주 조회되지만 자주 변경되지 않는 데이터는 **캐시 레이어**에 저장하면 DB 부하를 크게 줄일 수 있습니다.

```python
# redis_cache.py -- Redis 캐시 레이어 패턴
import redis
import sqlite3
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_user_with_cache(db_path, user_id, ttl=300):
    """사용자 정보를 캐시에서 먼저 조회, 없으면 DB에서 조회 후 캐시에 저장"""
    cache_key = f"user:{user_id}"

    # ── 캐시 확인 (Cache Hit) ──
    cached = redis_client.get(cache_key)
    if cached:
        print(f"캐시 히트: user:{user_id}")
        return json.loads(cached)

    # ── DB 조회 (Cache Miss) ──
    print(f"캐시 미스: DB 조회 user:{user_id}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user_data = {"id": row[0], "name": row[1], "email": row[2]}
        # ── 캐시에 저장 (TTL 5분) ──
        redis_client.setex(cache_key, ttl, json.dumps(user_data, ensure_ascii=False))
        return user_data
    return None

def invalidate_user_cache(user_id):
    """사용자 데이터 변경 시 캐시 무효화"""
    redis_client.delete(f"user:{user_id}")
```

### 캐시 레이어 아키텍처

```mermaid
flowchart TB
    CLIENT[클라이언트 요청]
    API[API 서버]
    CACHE{Redis 캐시\n확인}
    HIT[캐시 히트\n즉시 반환]
    MISS[캐시 미스]
    DB[(데이터베이스)]
    STORE[캐시에 저장\nTTL 설정]
    RESP[응답 반환]

    CLIENT --> API
    API --> CACHE
    CACHE -->|데이터 있음| HIT
    CACHE -->|데이터 없음| MISS
    MISS --> DB
    DB --> STORE
    STORE --> RESP
    HIT --> RESP
    RESP --> CLIENT

    style CLIENT fill:#fd79a8,stroke:#e84393,color:#fff
    style API fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style CACHE fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style HIT fill:#55efc4,stroke:#00b894,color:#2d3436
    style MISS fill:#e17055,stroke:#fab1a0,color:#fff
    style DB fill:#0984e3,stroke:#74b9ff,color:#fff
    style STORE fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style RESP fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 캐싱 전략별 장단점 비교

| 전략 | 방식 | 장점 | 단점 | 적합한 상황 |
|------|------|------|------|-------------|
| TTL 기반 | 일정 시간 후 자동 만료 | 구현 단순 | 만료 전까지 오래된 데이터 반환 가능 | 실시간성 덜 중요한 데이터 |
| Write-Through | 쓸 때 DB와 캐시 동시 갱신 | 항상 최신 데이터 | 쓰기 비용 증가 | 읽기가 많고 일관성 중요 |
| Write-Behind | 캐시에 먼저 쓰고 비동기 DB 반영 | 쓰기 성능 최대화 | 장애 시 데이터 손실 위험 | 쓰기가 매우 많은 경우 |
| Cache-Aside | 읽을 때만 캐시 사용 | 구현 직관적 | Cache Miss 시 지연 | 가장 일반적인 패턴 |

> **핵심 포인트:** 캐시는 "항상 최신이 아닐 수 있다"는 점을 설계에 반영해야 합니다. 금액, 재고, 인증 정보 등 정확성이 매우 중요한 데이터는 캐시 없이 DB를 직접 조회하거나, 캐시 TTL을 매우 짧게 설정해야 합니다.

---

## 8. 데이터베이스 섹션 총정리

### 04_database 섹션 13강의 학습 흐름

이번 섹션은 데이터베이스의 가장 기초적인 개념부터 시작하여 실무 수준의 최적화와 바이너리 데이터 관리까지 순차적으로 다루었습니다.

| 강의 번호 | 주제 | 핵심 내용 |
|-----------|------|-----------|
| 01 | 데이터베이스 기초 | DBMS 개념, 관계형 vs 비관계형 |
| 02 | RDBMS 개념 | 테이블, 관계, ERD |
| 03 | SQL 기초 (SQLite) | SELECT, INSERT, UPDATE, DELETE |
| 04 | SQL 심화 | JOIN, 서브쿼리, 집계 함수 |
| 05 | 키, 제약, 인덱스 | PK, FK, UNIQUE, INDEX |
| 06 | 정규화와 트랜잭션 | 1NF~3NF, ACID |
| 07 | Python DB 연동 | sqlite3, SQLAlchemy, ORM |
| 08 | MySQL과 프로덕션 DB | 서버 구조, Docker 환경 |
| 09 | PostgreSQL 심화 | JSONB, Full Text Search |
| 10 | NoSQL 개요 | MongoDB, Redis, 특성 비교 |
| 11 | 벡터 데이터베이스 이론 | 임베딩, 유사도 검색, ANN |
| 12 | 벡터 DB 실습 | ChromaDB, pgvector, FAISS |
| 13 | 바이너리 저장과 성능 | BLOB, 파일경로, 쿼리최적화 |

### 전체 학습 로드맵

```mermaid
flowchart TB
    SEC04[04_database 섹션\n13개 강의]

    SEC04 --> G1[기초 이론\n강의 01-02]
    SEC04 --> G2[SQL 실습\n강의 03-04]
    SEC04 --> G3[설계와 품질\n강의 05-06]
    SEC04 --> G4[실무 연동\n강의 07-08]
    SEC04 --> G5[확장과 다양성\n강의 09-10]
    SEC04 --> G6[AI 데이터\n강의 11-12]
    SEC04 --> G7[성능과 최적화\n강의 13]

    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5
    G5 --> G6
    G6 --> G7
    G7 --> NEXT[05_genai_advanced\n생성형 AI 심화]

    style SEC04 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style G1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G3 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G4 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G5 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G6 fill:#fd79a8,stroke:#e84393,color:#fff
    style G7 fill:#e17055,stroke:#fab1a0,color:#fff
    style NEXT fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 다음 단계: 05_genai_advanced와의 연결

04_database 섹션에서 학습한 내용은 `05_genai_advanced` 섹션의 핵심 기반이 됩니다.

| 04_database 학습 내용 | 05_genai_advanced 활용 |
|-----------------------|------------------------|
| 벡터 데이터베이스 (강의 11-12) | RAG(검색 증강 생성) 구현 |
| SQL과 Python 연동 (강의 07) | LangChain의 DB 체인 구성 |
| NoSQL (강의 10) | 대화 히스토리, 세션 관리 |
| 파일 경로 / 클라우드 저장 (강의 13) | 멀티모달 AI 입출력 관리 |
| 쿼리 최적화 (강의 13) | AI 서비스 응답 속도 개선 |
| 커넥션 풀 / 캐싱 (강의 13) | 고트래픽 AI API 서버 운영 |

> **핵심 포인트:** 데이터베이스는 AI 서비스의 "기억 장치"입니다. 벡터 DB는 의미적 기억을, RDBMS는 구조적 기억을, Redis는 단기 기억을 담당합니다. 이 세 가지를 조합하면 강력한 AI 서비스 백엔드를 구축할 수 있습니다.

---

## 9. 핵심 정리

### BLOB vs 파일경로 비교 요약

| 항목 | BLOB | 파일 경로 | 클라우드 스토리지 |
|------|------|-----------|------------------|
| 저장 위치 | DB 내부 | 로컬 파일시스템 | S3 / GCS 등 |
| 일관성 | 완벽 (트랜잭션) | 수동 관리 | 수동 관리 |
| 확장성 | 낮음 | 중간 | 매우 높음 |
| CDN 연동 | 불가 | 가능 | 기본 제공 |
| 비용 | DB 용량 비용 | 서버 디스크 비용 | 스토리지 + 전송 비용 |
| 권장 파일 크기 | ~1 MB | ~수백 MB | 제한 없음 |
| 권장 상황 | 소규모, 단순성 우선 | 중소규모, 단일 서버 | 대규모, 다중 서버 |

### 쿼리 최적화 핵심 체크리스트

아래 항목을 순서대로 점검하면 대부분의 쿼리 성능 문제를 해결할 수 있습니다.

1. `EXPLAIN QUERY PLAN` / `EXPLAIN ANALYZE`로 실행 계획 확인
2. Full Table Scan 발생 시 적절한 인덱스 추가
3. `SELECT *` 대신 필요한 컬럼만 명시
4. `WHERE` 절의 조건 컬럼에 인덱스 적용 여부 확인
5. `LIKE '%keyword%'` 패턴은 인덱스가 무효화됨 — 전문 검색(Full Text Search) 고려
6. 루프 내 반복 쿼리는 `IN` 절 또는 `JOIN`으로 통합 (N+1 해결)
7. 정렬(`ORDER BY`) 대상 컬럼에 인덱스 존재 여부 확인
8. 자주 조회되는 데이터는 Redis 캐시 레이어 추가

### 전체 DB 섹션 핵심 개념 요약

| 개념 분류 | 핵심 키워드 | 실무 활용 |
|-----------|-------------|-----------|
| 관계형 DB | 테이블, 기본키, 외래키, 정규화 | 사용자, 상품, 주문 데이터 |
| SQL | SELECT, JOIN, 집계, 인덱스 | 데이터 조회 및 분석 |
| 트랜잭션 | ACID, 격리 수준, 잠금 | 결제, 재고 감소 원자성 보장 |
| ORM | SQLAlchemy, Django ORM | Python 객체로 DB 조작 |
| NoSQL | 문서형, 키-값, 그래프 | 유연한 스키마, 고성능 캐시 |
| 벡터 DB | 임베딩, 코사인 유사도, ANN | 의미 검색, RAG 구현 |
| 바이너리 저장 | BLOB, 파일경로, S3 | 이미지, 문서, 미디어 파일 |
| 성능 최적화 | 인덱스, 쿼리 튜닝, 캐싱 | 응답 속도 개선, 서버 비용 절감 |
| 용량 관리 | 파티셔닝, 아카이빙, VACUUM | 장기 운영, 비용 최적화 |

### Key Takeaways

이번 강의 그리고 04_database 섹션 전체를 통해 다음의 핵심 원칙을 기억하시기 바랍니다.

- **적합한 도구를 선택하십시오.** 모든 문제에 RDBMS가 최선이 아니며, 모든 파일을 BLOB으로 저장할 필요도 없습니다. 데이터의 성격과 서비스 규모에 맞는 전략을 선택해야 합니다.

- **측정하고 최적화하십시오.** 쿼리를 작성할 때마다 `EXPLAIN`으로 실행 계획을 확인하는 습관을 들이십시오. 추측이 아닌 데이터를 기반으로 최적화해야 합니다.

- **데이터의 생명주기를 설계하십시오.** 데이터는 생성되는 순간부터 삭제 또는 아카이빙되는 순간까지 관리되어야 합니다. 초기에 정책을 수립하지 않으면 나중에 더 큰 비용을 치르게 됩니다.

- **일관성과 성능은 트레이드오프입니다.** 캐시, NoSQL, 파티셔닝은 모두 어느 정도의 일관성을 희생하고 성능을 얻는 방식입니다. 그 트레이드오프를 이해하고 의식적으로 선택해야 합니다.

- **AI 서비스에서 데이터베이스는 기억 장치입니다.** 다음 섹션에서 배울 RAG, 에이전트, 멀티모달 AI는 모두 데이터베이스에 의존합니다. 이번 섹션에서 쌓은 기반이 AI 서비스 개발의 핵심 역량이 됩니다.

---

### 다음 강의 미리보기

`05_genai_advanced` 섹션에서는 다음 내용을 학습합니다.

- **RAG(Retrieval-Augmented Generation):** 벡터 DB와 LLM을 결합하여 최신 정보를 활용하는 검색 증강 생성 구현
- **LangChain / LlamaIndex:** AI 애플리케이션 개발 프레임워크 활용
- **프롬프트 엔지니어링 심화:** Chain-of-Thought, Few-Shot, ReAct 패턴
- **멀티모달 AI:** 이미지, 음성, 텍스트를 함께 처리하는 AI 서비스 개발
- **AI 에이전트:** 도구를 사용하고 계획을 수립하는 자율 AI 시스템 설계

04_database 섹션에서 학습한 데이터베이스 지식이 이 모든 주제의 기반이 됩니다.

---

> **이전 강의:** [벡터 데이터베이스 실습](12_vector_db_implementations.md)
>
> **다음 섹션:** [05. 생성형 AI 심화](../05_genai_advanced/)
