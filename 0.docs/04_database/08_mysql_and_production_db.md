# MySQL과 프로덕션 데이터베이스

> 연습장에서 공식 문서로 — SQLite를 넘어 실무 환경의 MySQL과 PostgreSQL을 이해하고, Docker로 개발 환경을 구성하며 프로덕션 데이터베이스 운영의 기초를 다집니다.

---

## 1. 프로덕션 데이터베이스란

### 개발용 DB와 프로덕션 DB의 차이

소프트웨어 개발에는 여러 단계의 환경이 존재합니다. 개발자가 로컬에서 코드를 작성하는 **개발(Development) 환경**, 배포 전 최종 검증을 수행하는 **스테이징(Staging) 환경**, 그리고 실제 사용자가 접근하는 **프로덕션(Production) 환경**이 그것입니다. 각 환경마다 요구하는 데이터베이스의 특성이 다릅니다.

**실생활 비유:** 학교에서 수업 중 메모를 적는 **연습장**과 법적 효력이 있는 **공식 계약서**의 차이를 생각해 보십시오. 연습장은 가볍고 빠르게 쓸 수 있지만, 여러 사람이 동시에 열람하거나 안전하게 보관하는 기능은 없습니다. 공식 문서는 작성 절차가 복잡하지만 보안, 무결성, 접근 제어가 철저합니다. SQLite가 연습장이라면, MySQL과 PostgreSQL은 공식 문서에 해당합니다.

| 특성 | SQLite (개발/학습) | MySQL / PostgreSQL (프로덕션) |
|------|-------------------|-------------------------------|
| 파일 구조 | 단일 파일 (`.db`) | 클라이언트-서버 구조 |
| 동시 접속 | 매우 제한적 | 수천~수만 동시 접속 지원 |
| 인증/권한 | 없음 (파일 권한만) | 사용자별 세밀한 권한 제어 |
| 복제/고가용성 | 불가 | Master-Slave 복제 지원 |
| 백업 | 파일 복사 | 온라인 백업, 포인트-인-타임 복구 |
| 설치 복잡도 | 없음 (내장) | 서버 설치 및 구성 필요 |
| 적합한 상황 | 개발, 테스트, 임베디드 | 웹 서비스, 기업 시스템 |

### 프로덕션 DB에 요구되는 핵심 기능

실제 서비스를 운영하는 데이터베이스는 다음 네 가지 요건을 반드시 충족해야 합니다.

**동시 접속(Concurrency):** 수천 명의 사용자가 동시에 데이터를 읽고 쓸 때 충돌 없이 처리합니다. 이를 위해 트랜잭션 격리 수준과 잠금(Lock) 메커니즘이 필요합니다.

**인증과 권한(Authentication & Authorization):** 사용자별로 어떤 데이터베이스, 테이블에 어떤 작업(SELECT, INSERT, UPDATE, DELETE)을 허용할지 세밀하게 제어합니다.

**복제(Replication):** 데이터를 여러 서버에 복사하여 한 서버가 장애가 나도 서비스가 중단되지 않게 합니다. 읽기 요청을 여러 복제본에 분산하여 성능을 높이기도 합니다.

**백업과 복구(Backup & Recovery):** 데이터 손실에 대비하여 정기적으로 백업을 수행하고, 장애 발생 시 특정 시점으로 복구할 수 있는 PITR(Point-In-Time Recovery) 기능을 제공합니다.

### 개발 단계별 DB 선택 흐름

```mermaid
flowchart TB
    A["프로젝트 시작"]
    B["개발 환경\nDevelopment"]
    C["스테이징 환경\nStaging"]
    D["프로덕션 환경\nProduction"]
    E["SQLite\n빠른 프로토타이핑"]
    F["MySQL / PostgreSQL\n(Docker)"]
    G["MySQL / PostgreSQL\n(클라우드 또는 전용 서버)"]
    H["동시 접속 수 예상"]
    I["1~수십 명\n소규모"]
    J["수백~수만 명\n중대규모"]
    K["MySQL\n웹 서비스 최적화"]
    L["PostgreSQL\n복잡한 쿼리 / 확장성"]

    A --> B
    B --> C
    C --> D
    B --> E
    C --> F
    D --> G
    D --> H
    H --> I
    H --> J
    I --> K
    J --> L

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#e17055,stroke:#fab1a0,color:#fff
    style E fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style F fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style G fill:#fab1a0,stroke:#e17055,color:#2d3436
    style H fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style I fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style J fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style K fill:#55efc4,stroke:#00b894,color:#2d3436
    style L fill:#fd79a8,stroke:#e84393,color:#fff
```

> **핵심 포인트:** SQLite는 개발 초기 단계에서 빠른 실험을 위해 탁월합니다. 그러나 여러 사용자가 동시에 접속하는 실제 서비스에는 클라이언트-서버 구조의 MySQL 또는 PostgreSQL이 필수입니다.

---

## 2. MySQL 소개

### MySQL의 역사

MySQL은 1995년 스웨덴 회사 **MySQL AB**에서 Michael Widenius, David Axmark, Allan Larsson이 개발했습니다. 오픈소스로 배포되면서 PHP와 결합해 LAMP 스택(Linux, Apache, MySQL, PHP)의 핵심이 되었고, 초창기 웹 서비스 붐의 중심에 섰습니다.

2008년 **Sun Microsystems**가 MySQL AB를 10억 달러에 인수했고, 2010년 Oracle이 Sun을 인수하면서 MySQL도 Oracle 산하로 들어갔습니다. Oracle의 상업적 방향성에 우려를 느낀 원래 개발자 Michael Widenius가 MySQL을 포크(fork)하여 **MariaDB**를 만들었습니다.

| 구분 | MySQL | MariaDB |
|------|-------|---------|
| 소유권 | Oracle Corporation | MariaDB Foundation (오픈소스) |
| 라이선스 | GPL + 상용 라이선스 | GPL (완전 오픈소스) |
| 호환성 | MySQL 표준 | MySQL과 높은 호환성 |
| 개발 방향 | 기업 기능 강화 | 커뮤니티 주도 개발 |
| 기본 스토리지 엔진 | InnoDB | InnoDB (Aria 추가) |
| 활용 사례 | 대기업, 클라우드 서비스 | 많은 Linux 배포판 기본 DB |

### MySQL의 핵심 특징

**클라이언트-서버 모델:** MySQL은 서버 프로세스(`mysqld`)가 항상 실행 중이며, 클라이언트(애플리케이션, CLI 도구, GUI 도구)가 네트워크를 통해 서버에 연결하여 쿼리를 전송합니다. 이 구조 덕분에 여러 클라이언트가 동시에 같은 데이터에 접근할 수 있습니다.

**멀티스레드 아키텍처:** MySQL 서버는 각 클라이언트 연결마다 별도의 스레드를 생성합니다. 스레드 풀을 통해 수많은 동시 연결을 효율적으로 처리합니다.

**플러그인 가능한 스토리지 엔진:** MySQL의 독특한 점은 데이터를 실제로 저장하고 관리하는 **스토리지 엔진**을 교체할 수 있다는 것입니다. 용도에 따라 다른 엔진을 선택할 수 있습니다.

### MySQL 아키텍처

```mermaid
flowchart TD
    subgraph clients["클라이언트 계층"]
        C1["웹 애플리케이션\n(Python / Java)"]
        C2["MySQL CLI\nmysql -u user -p"]
        C3["GUI 도구\n(DBeaver / Workbench)"]
    end

    subgraph server["MySQL 서버 계층"]
        CONN["연결 관리자\nConnection Manager"]
        AUTH["인증 / 권한 관리\nAuthentication"]
        PARSER["SQL 파서\nParser"]
        OPTIMIZER["쿼리 옵티마이저\nQuery Optimizer"]
        CACHE["쿼리 캐시\nQuery Cache"]
    end

    subgraph engine["스토리지 엔진 계층"]
        INNODB["InnoDB\n(기본, ACID 보장)"]
        MYISAM["MyISAM\n(레거시, 빠른 읽기)"]
        MEMORY["MEMORY\n(인메모리, 임시 데이터)"]
    end

    subgraph storage["물리 저장소"]
        DISK["디스크 파일\n(.ibd, .frm)"]
    end

    C1 --> CONN
    C2 --> CONN
    C3 --> CONN
    CONN --> AUTH
    AUTH --> PARSER
    PARSER --> OPTIMIZER
    OPTIMIZER --> CACHE
    OPTIMIZER --> INNODB
    OPTIMIZER --> MYISAM
    OPTIMIZER --> MEMORY
    INNODB --> DISK
    MYISAM --> DISK

    style C1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style C2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style C3 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style CONN fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style AUTH fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style PARSER fill:#0984e3,stroke:#74b9ff,color:#fff
    style OPTIMIZER fill:#0984e3,stroke:#74b9ff,color:#fff
    style CACHE fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style INNODB fill:#55efc4,stroke:#00b894,color:#2d3436
    style MYISAM fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style MEMORY fill:#fd79a8,stroke:#e84393,color:#fff
    style DISK fill:#e17055,stroke:#fab1a0,color:#fff
```

### 스토리지 엔진: InnoDB vs MyISAM

현재 MySQL의 기본 스토리지 엔진은 **InnoDB**입니다. 과거에는 MyISAM이 널리 쓰였지만, 현대 애플리케이션에는 InnoDB를 사용하는 것이 표준입니다.

| 특성 | InnoDB | MyISAM |
|------|--------|--------|
| ACID 트랜잭션 | 지원 | 미지원 |
| 외래 키 | 지원 | 미지원 |
| 행 단위 잠금 | 지원 (Row-level Lock) | 테이블 단위 잠금만 |
| 크래시 복구 | 자동 복구 (Redo Log) | 수동 복구 필요 |
| 전문 검색 | MySQL 5.6+ 지원 | 기본 지원 |
| 읽기 성능 | 트랜잭션 오버헤드 존재 | 단순 읽기에서 빠름 |
| 쓰기 성능 | 동시 쓰기에 강함 | 단일 쓰기에서 빠름 |
| 적합한 용도 | 일반적인 웹 서비스 | 읽기 전용 로그 (레거시) |

> **핵심 포인트:** 새로운 프로젝트에서는 항상 InnoDB를 사용하십시오. InnoDB는 트랜잭션, 외래 키, 행 단위 잠금을 모두 지원하여 데이터 무결성과 동시성을 보장합니다.

---

## 3. Docker로 MySQL 설치하기

### Docker란 무엇인가

**실생활 비유:** Docker 컨테이너는 **이삿짐 컨테이너 박스**와 같습니다. 이삿짐 컨테이너에 가구, 전자제품, 생활용품을 모두 담아서 어느 항구에 내려도 동일한 내용물이 보장됩니다. Docker 컨테이너는 애플리케이션과 그것이 필요한 모든 라이브러리, 설정 파일을 하나의 단위로 묶어서, 어떤 서버(로컬 개발 노트북이든 클라우드 서버든)에서도 동일하게 실행됩니다.

Docker를 사용하면 MySQL을 직접 서버에 설치하지 않아도 됩니다. 명령어 한 줄로 원하는 버전의 MySQL을 즉시 실행하고, 필요 없으면 깨끗하게 제거할 수 있습니다.

### docker-compose.yml 작성

Docker Compose는 여러 컨테이너를 YAML 파일 하나로 정의하고 관리하는 도구입니다. MySQL 개발 환경을 위한 기본 설정은 다음과 같습니다.

```yaml
# docker-compose.yml -- MySQL 개발 환경
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: tutorial-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: tutorial_db
      MYSQL_USER: developer
      MYSQL_PASSWORD: devpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

각 설정 항목의 의미를 살펴보겠습니다.

| 설정 항목 | 설명 |
|-----------|------|
| `image: mysql:8.0` | Docker Hub에서 MySQL 8.0 공식 이미지를 사용 |
| `container_name` | 컨테이너에 붙이는 이름 (관리 편의성) |
| `MYSQL_ROOT_PASSWORD` | MySQL root 계정의 비밀번호 |
| `MYSQL_DATABASE` | 컨테이너 시작 시 자동 생성할 데이터베이스 이름 |
| `MYSQL_USER` | 일반 사용자 계정 이름 |
| `MYSQL_PASSWORD` | 일반 사용자 비밀번호 |
| `ports: "3306:3306"` | 호스트의 3306 포트를 컨테이너의 3306 포트에 연결 |
| `volumes` | 컨테이너가 삭제되어도 데이터가 남도록 영구 볼륨 사용 |

### Docker 주요 명령어

```bash
# 컨테이너를 백그라운드에서 시작
docker compose up -d

# 실행 중인 컨테이너 확인
docker compose ps

# 컨테이너 로그 확인
docker compose logs mysql

# 컨테이너를 중지하고 삭제 (볼륨은 유지)
docker compose down

# 컨테이너와 볼륨을 모두 삭제 (데이터 초기화)
docker compose down -v

# MySQL CLI에 직접 접속
docker exec -it tutorial-mysql mysql -u developer -pdevpassword tutorial_db
```

### MySQL CLI 접속 방법

컨테이너가 실행 중일 때, 다음 두 가지 방법으로 MySQL CLI에 접속할 수 있습니다.

```bash
# 방법 1: Docker exec를 통한 컨테이너 내부 접속
docker exec -it tutorial-mysql mysql -u developer -pdevpassword tutorial_db

# 방법 2: 호스트에서 직접 접속 (mysql 클라이언트가 설치된 경우)
mysql -h 127.0.0.1 -P 3306 -u developer -p tutorial_db

# 자주 사용하는 MySQL CLI 명령어
SHOW DATABASES;          -- 데이터베이스 목록
USE tutorial_db;         -- 데이터베이스 선택
SHOW TABLES;             -- 테이블 목록
DESCRIBE posts;          -- 테이블 구조 확인
```

### GUI 도구 소개

CLI가 불편하다면 그래픽 도구를 사용하여 MySQL을 관리할 수 있습니다.

| 도구 | 특징 | 적합한 대상 |
|------|------|-------------|
| DBeaver | 다양한 DB 지원, 무료, 크로스 플랫폼 | 개발자, 데이터 분석가 |
| MySQL Workbench | MySQL 공식 도구, 무료, 시각적 ER 다이어그램 | MySQL 전용 관리자 |
| TablePlus | 깔끔한 UI, 유료(기본 무료), macOS/Windows | 개인 개발자 |
| DataGrip | JetBrains 제품, 강력한 IDE 기능, 유료 | 전문 개발자 |

> **핵심 포인트:** Docker를 사용하면 MySQL 설치와 삭제가 명령어 하나로 해결됩니다. 개발 환경을 깨끗하게 유지하고 팀원 모두가 동일한 버전의 DB를 사용할 수 있습니다.

---

## 4. MySQL 기본 사용법

### 데이터베이스와 사용자 생성

MySQL에서는 먼저 데이터베이스(스키마)를 생성하고, 해당 데이터베이스에 접근할 수 있는 사용자를 만들어야 합니다.

```sql
-- 데이터베이스 생성 (문자 인코딩 지정)
CREATE DATABASE my_service
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 사용자 생성
CREATE USER 'app_user'@'%' IDENTIFIED BY 'secure_password';

-- 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON my_service.* TO 'app_user'@'%';

-- 권한 즉시 반영
FLUSH PRIVILEGES;
```

`utf8mb4`는 이모지를 포함한 모든 유니코드 문자를 지원합니다. MySQL의 `utf8`은 실제로 3바이트까지만 지원하는 불완전한 구현이므로, 반드시 `utf8mb4`를 사용해야 합니다.

### MySQL 주요 데이터 타입

| 분류 | 타입 | 설명 | 예시 |
|------|------|------|------|
| 정수 | `TINYINT` | 1바이트, -128~127 | 나이, 상태 코드 |
| 정수 | `INT` | 4바이트, 약 ±21억 | 일반 ID, 수량 |
| 정수 | `BIGINT` | 8바이트, 매우 큰 정수 | 트위터 ID, 금액 |
| 실수 | `DECIMAL(p,s)` | 정확한 소수점 | 금액, 비율 |
| 실수 | `FLOAT`, `DOUBLE` | 근사값 소수점 | 과학적 수치 |
| 문자 | `CHAR(n)` | 고정 길이 문자열 | 국가 코드, 성별 |
| 문자 | `VARCHAR(n)` | 가변 길이 문자열 | 이름, 이메일 |
| 문자 | `TEXT` | 긴 문자열 (최대 65KB) | 본문, 댓글 |
| 문자 | `LONGTEXT` | 매우 긴 문자열 (최대 4GB) | 대용량 문서 |
| 날짜 | `DATE` | 날짜만 (YYYY-MM-DD) | 생년월일 |
| 날짜 | `DATETIME` | 날짜+시간 | 게시 시간, 생성 시간 |
| 날짜 | `TIMESTAMP` | UTC 기준 저장, 시간대 자동 변환 | 로그 기록 |
| 기타 | `BOOLEAN` | TINYINT(1)의 별칭 | 활성화 여부 |
| 기타 | `JSON` | JSON 데이터 저장 (MySQL 5.7.8+) | 설정, 메타데이터 |

### SQLite vs MySQL 주요 문법 차이

| 항목 | SQLite | MySQL |
|------|--------|-------|
| 자동 증가 | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT AUTO_INCREMENT PRIMARY KEY` |
| 문자열 타입 | `TEXT` (하나로 통일) | `CHAR`, `VARCHAR`, `TEXT` 구분 |
| 불리언 | `INTEGER` (0/1) | `BOOLEAN` 또는 `TINYINT(1)` |
| 현재 시간 | `CURRENT_TIMESTAMP` | `CURRENT_TIMESTAMP` (동일) |
| 자동 업데이트 시간 | 트리거 필요 | `ON UPDATE CURRENT_TIMESTAMP` |
| 문자 인코딩 | 기본적으로 UTF-8 | `CHARACTER SET utf8mb4` 명시 권장 |
| 외래 키 | 기본 비활성, `PRAGMA` 활성화 | 기본 활성 (InnoDB) |
| 플레이스홀더 | `?` | `%s` (PyMySQL 기준) |
| IF NOT EXISTS | 지원 | 지원 |
| LIMIT/OFFSET | 지원 | 지원 |
| UPSERT | `INSERT OR REPLACE` | `INSERT ... ON DUPLICATE KEY UPDATE` |

### MySQL에서 게시판 테이블 생성

```sql
-- 게시판 테이블 (MySQL InnoDB)
CREATE TABLE IF NOT EXISTS posts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200)     NOT NULL,
    content     TEXT             NOT NULL,
    author      VARCHAR(50)      NOT NULL,
    view_count  INT              NOT NULL DEFAULT 0,
    is_deleted  BOOLEAN          NOT NULL DEFAULT FALSE,
    created_at  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 댓글 테이블 (외래 키로 posts 참조)
CREATE TABLE IF NOT EXISTS comments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    post_id     INT              NOT NULL,
    content     TEXT             NOT NULL,
    author      VARCHAR(50)      NOT NULL,
    created_at  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_post
        FOREIGN KEY (post_id) REFERENCES posts(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 인덱스 생성 (자주 조회하는 컬럼)
CREATE INDEX idx_posts_author    ON posts(author);
CREATE INDEX idx_posts_created   ON posts(created_at DESC);
CREATE INDEX idx_comments_post   ON comments(post_id);
```

> **핵심 포인트:** MySQL에서 테이블을 생성할 때는 `ENGINE=InnoDB`와 `CHARSET=utf8mb4`를 명시하는 습관을 기르십시오. 한글을 포함한 다국어 데이터와 트랜잭션 무결성이 모두 보장됩니다.

---

## 5. Python에서 MySQL 연동

### PyMySQL과 mysql-connector-python

Python에서 MySQL에 연결하는 대표적인 라이브러리는 두 가지입니다.

| 라이브러리 | 특징 | 설치 |
|-----------|------|------|
| `PyMySQL` | 순수 Python 구현, 가볍고 설치 간단 | `pip install pymysql` |
| `mysql-connector-python` | Oracle 공식 라이브러리, C 확장 사용 | `pip install mysql-connector-python` |

본 강의에서는 설치가 간단하고 SQLAlchemy와 호환성이 좋은 **PyMySQL**을 사용합니다.

### SQLite 코드 vs MySQL 코드 비교

```python
# sqlite_example.py -- SQLite 연결 방식
import sqlite3

conn = sqlite3.connect("local.db")
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO posts (title, content) VALUES (?, ?)",  # ? 플레이스홀더
    ("제목", "내용")
)
conn.commit()
conn.close()
```

```python
# mysql_example.py -- MySQL 연결 방식 (PyMySQL)
import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='developer',
    password='devpassword',
    database='tutorial_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO posts (title, content) VALUES (%s, %s)",  # %s 플레이스홀더
    ("제목", "내용")
)
conn.commit()
conn.close()
```

가장 큰 차이는 **연결 방식**과 **플레이스홀더** 문자(`?` → `%s`)입니다. 나머지 SQL 문법과 커밋/롤백 패턴은 동일합니다.

### Python MySQL 연결 흐름

```mermaid
flowchart TB
    A["앱 시작"] --> B["pymysql.connect 호출"]
    B --> C{"연결 성공?"}
    C -- "실패" --> D["OperationalError"]
    C -- "성공" --> E["cursor 생성"] --> F["execute SQL"]
    F --> G["SELECT 읽기"]
    F --> H["INSERT/UPDATE/DELETE"]
    G --> I["fetchall / fetchone"] --> N["결과 반환"]
    H --> J["commit"]
    H --> L{"예외?"}
    L -->|"예"| K["rollback"]
    J --> M["close"]
    K --> M

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#e17055,stroke:#fab1a0,color:#fff
    style E fill:#0984e3,stroke:#74b9ff,color:#fff
    style F fill:#a29bfe,stroke:#6c5ce7,color:#2d3436
    style G fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style H fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style I fill:#55efc4,stroke:#00b894,color:#2d3436
    style J fill:#55efc4,stroke:#00b894,color:#2d3436
    style K fill:#e17055,stroke:#fab1a0,color:#fff
    style L fill:#fd79a8,stroke:#e84393,color:#fff
    style M fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style N fill:#55efc4,stroke:#00b894,color:#2d3436
```

### PyMySQL 기본 사용 코드

```python
# mysql_basics.py -- PyMySQL 기본 사용법
import pymysql

connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='developer',
    password='devpassword',
    database='tutorial_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # ── 테이블 생성 ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(50) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── INSERT ──
        cursor.execute(
            "INSERT INTO posts (title, content, author) VALUES (%s, %s, %s)",
            ("첫 번째 글", "MySQL에서 작성한 첫 글입니다", "홍길동")
        )
    connection.commit()

    with connection.cursor() as cursor:
        # ── SELECT 전체 조회 ──
        cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
        posts = cursor.fetchall()
        for post in posts:
            print(f"[{post['id']}] {post['title']} - {post['author']}")

        # ── SELECT 단건 조회 ──
        cursor.execute("SELECT * FROM posts WHERE id = %s", (1,))
        post = cursor.fetchone()
        if post:
            print(f"제목: {post['title']}, 내용: {post['content']}")

    with connection.cursor() as cursor:
        # ── UPDATE ──
        affected = cursor.execute(
            "UPDATE posts SET title = %s WHERE id = %s",
            ("수정된 제목", 1)
        )
        print(f"{affected}개 행이 수정되었습니다")
    connection.commit()

    with connection.cursor() as cursor:
        # ── DELETE ──
        affected = cursor.execute(
            "DELETE FROM posts WHERE id = %s", (1,)
        )
        print(f"{affected}개 행이 삭제되었습니다")
    connection.commit()

except pymysql.MySQLError as e:
    print(f"MySQL 오류 발생: {e}")
    connection.rollback()
finally:
    connection.close()
```

`DictCursor`를 사용하면 결과가 튜플 대신 딕셔너리 형태로 반환되어 `row['column_name']` 방식으로 편리하게 접근할 수 있습니다.

> **핵심 포인트:** `try-finally` 블록으로 항상 `connection.close()`를 보장하고, 쓰기 작업 후에는 반드시 `commit()`을 호출하십시오. 오류 발생 시 `rollback()`으로 부분 변경을 원래대로 되돌립니다.

---

## 6. PostgreSQL 소개

### PostgreSQL의 특징

PostgreSQL(포스트그레SQL, 흔히 "포스트그레스"로 불림)은 1986년 UC 버클리의 POSTGRES 프로젝트에서 출발했습니다. 1996년 SQL 지원을 추가하면서 PostgreSQL로 이름이 바뀌었습니다. 완전한 오픈소스이며 어떠한 기업 소유도 아닙니다.

PostgreSQL은 스스로를 **"세계에서 가장 발전된 오픈소스 관계형 데이터베이스"**라고 칭합니다. 그만큼 고급 SQL 기능과 확장성 면에서 MySQL을 앞섭니다.

**실생활 비유:** MySQL이 **빠르고 믿음직한 시내버스**라면, PostgreSQL은 **다목적 고급 기차**에 해당합니다. 시내버스는 일상적인 이동에 충분하고 빠릅니다. 고급 기차는 더 많은 짐을 싣고, 더 멀리 가며, 화물칸을 추가(확장)할 수 있습니다. 단, 시내버스보다 복잡하게 운영됩니다.

### MySQL vs PostgreSQL 비교

| 항목 | MySQL | PostgreSQL |
|------|-------|------------|
| 라이선스 | GPL + 상용 | PostgreSQL License (자유로운 상용 사용) |
| 개발 주체 | Oracle + 커뮤니티 | 글로벌 자원봉사자 커뮤니티 |
| SQL 표준 준수 | 부분 준수 | 높은 SQL 표준 준수 |
| 데이터 타입 | 기본 타입 위주 | JSONB, 배열, UUID, hstore 등 풍부 |
| 확장 기능 | 제한적 | 확장(Extension) 시스템으로 무한 확장 |
| Window Functions | MySQL 8.0+ 지원 | 완전 지원 (오래전부터) |
| CTE (WITH 절) | MySQL 8.0+ 지원 | 완전 지원 |
| JSONB | 미지원 (JSON만) | 바이너리 JSON으로 인덱싱 가능 |
| 벡터 검색 | 미지원 | pgvector 확장으로 지원 |
| 파티셔닝 | 지원 | 더 강력하게 지원 |
| 읽기 성능 | 단순 쿼리에서 빠름 | 복잡한 쿼리에서 강함 |
| 커뮤니티 인기도 | 웹 개발 전통적 강세 | 데이터 엔지니어링/AI 분야 급성장 |

### PostgreSQL 고급 기능

**JSONB (Binary JSON):** 일반 JSON 컬럼과 달리, JSONB는 바이너리 형태로 저장하여 인덱스를 생성하고 빠르게 조회할 수 있습니다.

```sql
-- PostgreSQL JSONB 예시
CREATE TABLE products (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(200) NOT NULL,
    attrs   JSONB
);

-- JSON 내부 필드로 인덱스 생성 가능
CREATE INDEX idx_products_category ON products ((attrs->>'category'));

-- JSON 경로로 조회
SELECT name, attrs->>'color' AS color
FROM products
WHERE attrs->>'category' = '전자제품'
  AND (attrs->>'price')::INT < 100000;
```

**pgvector 확장 (벡터 검색):** AI 시대에 등장한 중요한 확장으로, PostgreSQL을 벡터 데이터베이스로 활용할 수 있게 합니다. 텍스트 임베딩(embedding) 벡터를 저장하고 코사인 유사도 검색이 가능합니다. 이 기능은 11강(벡터 데이터베이스)과 12강(RAG 시스템)에서 상세히 다룹니다.

```sql
-- pgvector 확장 활성화 (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS vector;

-- 1536차원 벡터를 저장하는 테이블 (OpenAI 임베딩 기준)
CREATE TABLE documents (
    id        SERIAL PRIMARY KEY,
    content   TEXT,
    embedding VECTOR(1536)
);

-- 코사인 유사도 기반 검색
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

### RDBMS 선택 가이드

```mermaid
flowchart LR
    A["DB 선택"] --> B{"프로젝트 규모?"}
    B -- "소규모" --> E["SQLite"]
    B -- "중대규모" --> F{"요구사항?"}
    F -- "단순 CRUD" --> I["MySQL / MariaDB"]
    F -- "복잡/AI/확장" --> J["PostgreSQL"]
    I --> K["일반 웹앱, 쇼핑몰"]
    J --> L["데이터 분석, AI, GIS"]

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style F fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style I fill:#55efc4,stroke:#00b894,color:#2d3436
    style J fill:#fd79a8,stroke:#e84393,color:#fff
    style K fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style L fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 언제 무엇을 선택하는가

| 상황 | 추천 DB | 이유 |
|------|---------|------|
| 개인 블로그, 소규모 앱 | SQLite | 설치 불필요, 관리 부담 없음 |
| WordPress, 일반 쇼핑몰 | MySQL | 생태계 성숙, 호스팅 지원 풍부 |
| 스타트업 SaaS 서비스 | PostgreSQL | 확장성, 고급 SQL, pgvector |
| 데이터 분석 / 리포팅 | PostgreSQL | Window Function, CTE 완전 지원 |
| AI 임베딩 / 벡터 검색 | PostgreSQL + pgvector | 벡터 인덱싱과 SQL 쿼리 통합 |
| 대규모 읽기 트래픽 | MySQL + 복제 | 읽기 복제본 분산 처리 |
| 지리 정보 (GIS) | PostgreSQL + PostGIS | 강력한 공간 데이터 지원 |

> **핵심 포인트:** MySQL은 검증된 웹 서비스 백엔드로 안정적입니다. PostgreSQL은 SQL 표준 준수율이 높고 pgvector 같은 강력한 확장이 가능하여 AI 시대에 급속도로 인기가 높아지고 있습니다.

---

## 7. 데이터베이스 운영 기초

### 백업과 복원

**mysqldump**는 MySQL 데이터를 SQL 파일로 덤프하는 공식 도구입니다. 생성된 파일에는 테이블 생성 스크립트와 INSERT 문이 포함되어 있어 다른 서버로 이전할 때도 유용합니다.

```bash
# 전체 데이터베이스 백업
mysqldump -u developer -p tutorial_db > backup_$(date +%Y%m%d).sql

# Docker 컨테이너에서 백업
docker exec tutorial-mysql mysqldump -u developer -pdevpassword tutorial_db \
  > backup_$(date +%Y%m%d).sql

# 특정 테이블만 백업
mysqldump -u developer -p tutorial_db posts comments > posts_backup.sql

# 백업 복원
mysql -u developer -p tutorial_db < backup_20240101.sql

# Docker 컨테이너에서 복원
docker exec -i tutorial-mysql mysql -u developer -pdevpassword tutorial_db \
  < backup_20240101.sql
```

### 복제(Replication): Master-Slave 구조

**실생활 비유:** 유명 레스토랑이 한 지점에서 성공하면 여러 지점을 낸다고 생각해 보십시오. 본점(Master)에서 새로운 메뉴를 개발하면 모든 지점(Slave)이 동일한 메뉴를 제공합니다. 손님은 가까운 지점에서 식사하면 됩니다. Master DB에서 쓰기 작업이 일어나면 Slave DB들이 동기화되고, 읽기 요청은 여러 Slave에 분산됩니다.

```mermaid
flowchart TB
    APP["웹 애플리케이션"]
    LB["로드 밸런서\n(읽기 분산)"]
    MASTER["Master DB\n(쓰기 전용)"]
    SLAVE1["Slave DB 1\n(읽기 전용)"]
    SLAVE2["Slave DB 2\n(읽기 전용)"]
    SLAVE3["Slave DB 3\n(읽기 전용)"]
    BINLOG["Binary Log\n(변경 이벤트 기록)"]
    RELAY["Relay Log\n(복제 로그)"]

    APP -- "INSERT/UPDATE/DELETE" --> MASTER
    APP -- "SELECT" --> LB
    LB --> SLAVE1
    LB --> SLAVE2
    LB --> SLAVE3
    MASTER --> BINLOG
    BINLOG -- "비동기 복제" --> RELAY
    RELAY --> SLAVE1
    RELAY --> SLAVE2
    RELAY --> SLAVE3

    style APP fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style LB fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style MASTER fill:#e17055,stroke:#fab1a0,color:#fff
    style SLAVE1 fill:#55efc4,stroke:#00b894,color:#2d3436
    style SLAVE2 fill:#55efc4,stroke:#00b894,color:#2d3436
    style SLAVE3 fill:#55efc4,stroke:#00b894,color:#2d3436
    style BINLOG fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style RELAY fill:#74b9ff,stroke:#0984e3,color:#2d3436
```

### 커넥션 풀링

데이터베이스 연결은 비용이 큰 작업입니다. 매 요청마다 새 연결을 맺고 끊으면 성능이 크게 저하됩니다. **커넥션 풀(Connection Pool)**은 미리 여러 연결을 맺어 두고, 요청이 올 때 기존 연결을 재사용하는 기법입니다.

```python
# connection_pool.py -- SQLAlchemy 커넥션 풀 설정
from sqlalchemy import create_engine

# MySQL 연결 풀 (권장)
engine = create_engine(
    "mysql+pymysql://developer:devpassword@localhost:3306/tutorial_db"
    "?charset=utf8mb4",
    pool_size=10,          # 기본 연결 수
    max_overflow=20,       # 최대 추가 연결 수
    pool_timeout=30,       # 연결 대기 시간 (초)
    pool_recycle=3600,     # 1시간마다 연결 갱신 (MySQL의 wait_timeout 대응)
    echo=False             # SQL 로깅 비활성화
)
```

### 모니터링 기초

운영 중인 MySQL의 상태를 확인하는 기본 명령어입니다.

```sql
-- 현재 실행 중인 쿼리 목록
SHOW PROCESSLIST;

-- 슬로우 쿼리 로그 설정 (1초 이상 걸리는 쿼리 기록)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 테이블 크기 확인
SELECT
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb
FROM information_schema.tables
WHERE table_schema = 'tutorial_db'
ORDER BY data_length DESC;

-- 인덱스 사용 여부 확인 (EXPLAIN)
EXPLAIN SELECT * FROM posts WHERE author = '홍길동';
```

### 보안 기본 수칙

**접근 제어:** 최소 권한 원칙을 따릅니다. 애플리케이션 계정에는 필요한 테이블에 대한 `SELECT`, `INSERT`, `UPDATE`, `DELETE` 권한만 부여하고, `DROP`, `ALTER` 같은 관리 권한은 부여하지 않습니다.

```sql
-- 좋지 않은 예: 모든 권한 부여
GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'%';

-- 올바른 예: 필요한 권한만 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON tutorial_db.* TO 'app_user'@'%';
```

**SQL Injection 방지:** 항상 파라미터화된 쿼리(Parameterized Query)를 사용하십시오. 이전 강의에서 배운 내용이지만, 가장 중요한 보안 원칙이므로 반복 강조합니다.

```python
# SQL Injection에 취약한 코드 (절대 사용 금지)
username = request.args.get('username')
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
# username = "' OR '1'='1" 입력 시 모든 행이 조회됨

# 올바른 파라미터화된 쿼리
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

**SSL 연결:** 네트워크를 통해 민감한 데이터가 오갈 때는 SSL/TLS를 통해 암호화합니다.

```python
# SSL 연결 설정
connection = pymysql.connect(
    host='production-db.example.com',
    user='app_user',
    password='secure_password',
    database='prod_db',
    ssl={'ca': '/path/to/ca-cert.pem'}
)
```

> **핵심 포인트:** 프로덕션 DB 운영의 핵심은 백업 자동화, 복제를 통한 고가용성, 커넥션 풀을 통한 성능 최적화, 그리고 최소 권한 원칙에 기반한 보안입니다. 이 네 가지가 기초입니다.

---

## 8. 핵심 정리

### SQLite vs MySQL vs PostgreSQL 종합 비교

| 항목 | SQLite | MySQL | PostgreSQL |
|------|--------|-------|------------|
| 구조 | 파일 기반 | 클라이언트-서버 | 클라이언트-서버 |
| 설치 | 불필요 (내장) | 서버 설치 필요 | 서버 설치 필요 |
| 동시 접속 | 매우 제한적 | 우수 | 우수 |
| ACID 트랜잭션 | 지원 | InnoDB 지원 | 완전 지원 |
| SQL 표준 준수 | 부분 | 부분 | 높음 |
| JSON 지원 | 미지원 | JSON | JSONB (인덱싱 가능) |
| 벡터 검색 | 미지원 | 미지원 | pgvector 확장 |
| 복제 | 미지원 | Master-Slave | 스트리밍 복제 |
| 커뮤니티 | 소규모 | 대형 | 대형 (AI 분야 급성장) |
| 클라우드 지원 | 제한적 | AWS RDS, GCP, Azure | AWS RDS, GCP, Azure |
| 학습 곡선 | 매우 낮음 | 낮음 | 중간 |
| 라이선스 | Public Domain | GPL / 상용 | 자유 오픈소스 |
| 주요 사용처 | 개발/테스트/임베디드 | 웹 서비스 전반 | 분석/AI/복잡한 서비스 |

### DB 선택 가이드라인

```mermaid
flowchart TB
    subgraph dev["개발/학습 단계"]
        D1["SQLite - 설치 없이 바로 시작"]
    end
    subgraph small["소규모 서비스"]
        S1["MySQL - Docker로 시작"]
    end
    subgraph medium["중대규모 서비스"]
        M1["MySQL + 읽기 복제본"]
        M2["PostgreSQL + 파티셔닝"]
    end
    subgraph ai["AI / 분석 서비스"]
        A1["PostgreSQL + pgvector + PostGIS"]
    end

    dev --> small
    small --> medium
    medium --> ai

    style D1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style S1 fill:#55efc4,stroke:#00b894,color:#2d3436
    style M1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style M2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style A1 fill:#fd79a8,stroke:#e84393,color:#fff
```

### 오늘 학습의 핵심 요약

| 주제 | 핵심 내용 |
|------|-----------|
| 프로덕션 DB 조건 | 동시 접속, 인증/권한, 복제, 백업 네 가지 필수 |
| MySQL 아키텍처 | 클라이언트-서버 구조, 플러그인 스토리지 엔진 |
| InnoDB | ACID 트랜잭션, 행 단위 잠금, 외래 키 지원 |
| Docker 활용 | `docker compose up -d` 한 줄로 MySQL 개발 환경 구성 |
| utf8mb4 | MySQL에서 한글 및 이모지를 위한 필수 문자 인코딩 |
| PyMySQL | SQLite와 동일한 패턴, 플레이스홀더만 `%s`로 변경 |
| PostgreSQL 강점 | JSONB, pgvector, 높은 SQL 표준 준수, AI 분야 확장성 |
| 운영 기초 | 정기 백업, 복제, 커넥션 풀, 최소 권한 원칙 |

### Day 21 학습 체크리스트

- Docker Compose로 MySQL 컨테이너를 직접 실행해 보셨습니까?
- PyMySQL로 CRUD를 SQLite와 비교하며 작성해 보셨습니까?
- InnoDB와 MyISAM의 차이를 설명할 수 있습니까?
- `utf8mb4`를 사용해야 하는 이유를 이해하셨습니까?
- MySQL과 PostgreSQL 중 어떤 상황에서 무엇을 선택할지 기준이 생겼습니까?

### 다음 강의 미리보기

다음 강의(22일차)에서는 **NoSQL 데이터베이스와 CAP 정리**를 다룹니다. 관계형 데이터베이스가 해결하지 못하는 문제들 — 극한적인 수평 확장, 유연한 스키마, 고속 캐싱 — 을 NoSQL이 어떻게 해결하는지 살펴봅니다. MongoDB(문서형), Redis(키-값), Elasticsearch(검색) 등 주요 NoSQL 데이터베이스의 특징과 CAP 이론을 통해 분산 시스템의 트레이드오프를 이해합니다.

---

> **이전 강의:** [Python 데이터베이스 연동](07_python_db_integration.md)
>
> **다음 강의:** [NoSQL과 CAP 정리](09_nosql_and_cap_theorem.md)
