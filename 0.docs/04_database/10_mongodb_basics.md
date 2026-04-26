# MongoDB 기초와 문서 지향 데이터베이스

> 행과 열의 세계를 벗어나 유연한 문서의 세계로 -- MongoDB CRUD, PyMongo, 그리고 Embedding vs Referencing 스키마 설계 전략을 실전 예제와 함께 익힙니다

---

## 1. MongoDB 소개

### 1.1 MongoDB란 무엇인가

MongoDB는 2009년 10X Gen(현 MongoDB Inc.)이 출시한 **문서 지향(Document-Oriented) NoSQL 데이터베이스**입니다. 이름 자체가 "Humongous(거대한) Database"에서 유래했을 만큼, 방대한 양의 비정형 데이터를 유연하고 빠르게 다루는 것을 목표로 설계되었습니다.

실생활 비유를 들자면, 관계형 데이터베이스(RDBMS)는 마치 **엑셀 스프레드시트**와 같습니다. 모든 행은 같은 열 구조를 따라야 하고, 값이 없으면 빈 칸이라도 있어야 합니다. 반면 MongoDB는 **서랍 속 파일 폴더**와 같습니다. 각 폴더(문서)는 저마다 다른 내용을 담을 수 있고, 어떤 폴더는 사진이 들어 있고 어떤 폴더는 계약서만 들어 있어도 전혀 문제가 없습니다.

### 1.2 RDBMS와 MongoDB 용어 비교

관계형 데이터베이스에 익숙한 개발자라면 아래 매핑 테이블을 통해 MongoDB의 개념을 빠르게 이해할 수 있습니다.

| RDBMS 개념 | MongoDB 개념 | 설명 |
|------------|--------------|------|
| Database | Database | 동일한 개념, 최상위 논리적 단위 |
| Table | Collection | 문서(Document)의 모음 |
| Row / Record | Document | JSON(BSON) 형태의 데이터 단위 |
| Column | Field | 문서 내 개별 키-값 쌍 |
| Primary Key | `_id` Field | 문서의 고유 식별자 (ObjectId) |
| INDEX | Index | 동일한 개념, 조회 성능 향상 |
| JOIN | Embedding / `$lookup` | 관계 데이터 처리 방식 |
| Schema | 스키마리스(Schemaless) | 필드 구조가 고정되지 않음 |
| Transaction | Multi-document Transaction | MongoDB 4.0 이상 지원 |
| SQL | MQL (MongoDB Query Language) | 쿼리 언어 |

### 1.3 BSON (Binary JSON) 형식

MongoDB는 데이터를 **BSON(Binary JSON)** 형식으로 저장합니다. JSON을 이진(Binary) 형식으로 인코딩한 것으로, 다음과 같은 장점을 제공합니다.

| 특성 | JSON | BSON |
|------|------|------|
| 형식 | 텍스트 | 이진(Binary) |
| 파싱 속도 | 상대적으로 느림 | 빠름 |
| 추가 데이터 타입 | 없음 | Date, ObjectId, Binary, Decimal128 등 |
| 문서 크기 정보 | 없음 | 문서 길이 포함 (빠른 스킵 가능) |
| 인간 가독성 | 높음 | 낮음 (이진 형식) |

> **핵심 포인트:** MongoDB는 개발자가 JSON으로 작성한 쿼리와 데이터를 내부적으로 BSON으로 변환하여 저장합니다. 개발자는 BSON을 직접 다룰 필요 없이 JSON처럼 사용하면 됩니다.

### 1.4 MongoDB 아키텍처

```mermaid
flowchart TB
    Client["클라이언트 (PyMongo / mongosh / Compass)"]
    Server["MongoDB Server\n(mongod 프로세스)"]
    DB1["Database\ntutorial_db"]
    DB2["Database\napp_db"]
    Col1["Collection\nposts"]
    Col2["Collection\nusers"]
    Col3["Collection\norders"]
    Doc1["Document\n{ _id, title, author, tags }"]
    Doc2["Document\n{ _id, title, author, tags }"]
    Doc3["Document\n{ _id, email, role }"]

    Client --> Server
    Server --> DB1
    Server --> DB2
    DB1 --> Col1
    DB1 --> Col2
    DB2 --> Col3
    Col1 --> Doc1
    Col1 --> Doc2
    Col2 --> Doc3

    style Client fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style Server fill:#0984e3,stroke:#74b9ff,color:#fff
    style DB1 fill:#e17055,stroke:#fab1a0,color:#fff
    style DB2 fill:#e17055,stroke:#fab1a0,color:#fff
    style Col1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Col2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Col3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Doc1 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Doc2 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Doc3 fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

---

## 2. Docker로 MongoDB 설치

### 2.1 docker-compose.yml 작성

로컬 개발 환경에서 MongoDB를 가장 빠르게 설치하는 방법은 Docker를 사용하는 것입니다. 아래 `docker-compose.yml` 파일을 작성하면 MongoDB 7.0을 즉시 실행할 수 있습니다.

```yaml
# docker-compose.yml -- MongoDB 개발 환경
version: '3.8'
services:
  mongodb:
    image: mongo:7.0
    container_name: tutorial-mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: adminpassword
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

컨테이너 실행과 중지는 다음 명령어를 사용합니다.

```bash
# 컨테이너 백그라운드 실행
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 중지
docker-compose down
```

### 2.2 mongosh (MongoDB Shell) 기본 명령어

`mongosh`는 MongoDB와 대화형으로 소통하는 공식 CLI 도구입니다. 아래와 같이 컨테이너에 접속하여 사용할 수 있습니다.

```bash
# 컨테이너 내부의 mongosh 실행
docker exec -it tutorial-mongo mongosh -u admin -p adminpassword --authenticationDatabase admin
```

mongosh에서 자주 사용하는 기본 명령어는 다음과 같습니다.

```javascript
// 데이터베이스 목록 확인
show dbs

// 데이터베이스 선택 또는 생성
use tutorial_db

// 현재 데이터베이스 확인
db

// 컬렉션 목록 확인
show collections

// 컬렉션 내 모든 문서 조회
db.posts.find()

// 결과를 보기 좋게 출력
db.posts.find().pretty()

// mongosh 종료
exit
```

### 2.3 GUI 도구: MongoDB Compass

터미널이 익숙하지 않다면 **MongoDB Compass**를 사용할 수 있습니다. MongoDB 공식 GUI 클라이언트로, 데이터 탐색, 쿼리 작성, 인덱스 관리, 집계 파이프라인 시각화 등 다양한 기능을 제공합니다.

접속 URI 형식은 다음과 같습니다.

```
mongodb://admin:adminpassword@localhost:27017/
```

> **핵심 포인트:** Docker를 사용하면 로컬 OS에 MongoDB를 직접 설치하지 않아도 됩니다. `docker-compose up -d` 명령 하나로 격리된 MongoDB 환경을 즉시 시작하고, `docker-compose down`으로 깔끔하게 종료할 수 있습니다.

---

## 3. MongoDB CRUD 기초

### 3.1 Create -- 문서 삽입

#### 3.1.1 문서 구조와 ObjectId

MongoDB의 모든 문서는 반드시 `_id` 필드를 가집니다. 삽입 시 `_id`를 지정하지 않으면 MongoDB가 자동으로 **ObjectId**를 생성합니다. ObjectId는 12바이트 BSON 타입으로, 타임스탬프(4바이트), 랜덤 값(5바이트), 증가 카운터(3바이트)로 구성되어 전역적으로 유일성을 보장합니다.

```javascript
// mongosh -- 단일 문서 삽입
db.posts.insertOne({
  title: "MongoDB 첫 글",
  content: "문서 지향 DB의 세계에 오신 것을 환영합니다",
  author: "홍길동",
  tags: ["mongodb", "nosql", "tutorial"],
  views: 0,
  created_at: new Date()
})

// mongosh -- 여러 문서 한번에 삽입
db.posts.insertMany([
  { title: "두 번째 글", author: "김철수", tags: ["python"], views: 10 },
  { title: "세 번째 글", author: "이영희", tags: ["database"], views: 5 }
])
```

### 3.2 Read -- 문서 조회

#### 3.2.1 기본 조회

```javascript
// mongosh -- 모든 문서 조회
db.posts.find()

// mongosh -- 조건 조회 (author가 홍길동인 문서)
db.posts.find({ author: "홍길동" })

// mongosh -- 단일 문서 조회 (첫 번째 매칭 결과만)
db.posts.findOne({ author: "홍길동" })
```

#### 3.2.2 쿼리 연산자

| 연산자 | 의미 | 예시 |
|--------|------|------|
| `$eq` | 같음 (기본값) | `{ views: { $eq: 0 } }` |
| `$ne` | 같지 않음 | `{ author: { $ne: "홍길동" } }` |
| `$gt` | 초과 | `{ views: { $gt: 10 } }` |
| `$gte` | 이상 | `{ views: { $gte: 10 } }` |
| `$lt` | 미만 | `{ views: { $lt: 100 } }` |
| `$lte` | 이하 | `{ views: { $lte: 100 } }` |
| `$in` | 배열 내 포함 | `{ author: { $in: ["홍길동", "김철수"] } }` |
| `$nin` | 배열 내 미포함 | `{ tags: { $nin: ["draft"] } }` |
| `$regex` | 정규식 매칭 | `{ title: { $regex: "MongoDB" } }` |
| `$exists` | 필드 존재 여부 | `{ image: { $exists: true } }` |
| `$and` | 논리 AND | `{ $and: [{ views: { $gt: 5 } }, { author: "홍길동" }] }` |
| `$or` | 논리 OR | `{ $or: [{ author: "홍길동" }, { author: "김철수" }] }` |

```javascript
// mongosh -- 복합 조건 조회
// views가 5 초과이고 tags에 "mongodb"가 포함된 문서
db.posts.find({
  views: { $gt: 5 },
  tags: "mongodb"
})

// mongosh -- 프로젝션 (필요한 필드만 조회)
// title과 author만 반환 (_id는 기본 포함)
db.posts.find(
  { author: "홍길동" },
  { title: 1, author: 1, _id: 0 }
)

// mongosh -- 정렬, 제한, 건너뛰기
db.posts.find()
  .sort({ created_at: -1 })  // 최신순 정렬 (-1: 내림차순)
  .skip(10)                   // 10개 건너뛰기 (페이징)
  .limit(5)                   // 5개만 반환
```

### 3.3 Update -- 문서 수정

#### 3.3.1 업데이트 연산자

| 연산자 | 의미 | 예시 |
|--------|------|------|
| `$set` | 필드 값 설정 (없으면 추가) | `{ $set: { title: "새 제목" } }` |
| `$unset` | 필드 삭제 | `{ $unset: { draft: "" } }` |
| `$inc` | 숫자 필드 증감 | `{ $inc: { views: 1 } }` |
| `$push` | 배열에 요소 추가 | `{ $push: { tags: "update" } }` |
| `$pull` | 배열에서 요소 제거 | `{ $pull: { tags: "draft" } }` |
| `$addToSet` | 중복 없이 배열에 추가 | `{ $addToSet: { tags: "nosql" } }` |
| `$rename` | 필드 이름 변경 | `{ $rename: { "old_name": "new_name" } }` |

```javascript
// mongosh -- 단일 문서 수정
db.posts.updateOne(
  { author: "홍길동" },
  {
    $set: { title: "수정된 제목" },
    $inc: { views: 1 },
    $push: { tags: "updated" }
  }
)

// mongosh -- 여러 문서 수정
db.posts.updateMany(
  { views: { $lt: 5 } },
  { $set: { status: "low_traffic" } }
)

// mongosh -- upsert (없으면 삽입, 있으면 수정)
db.posts.updateOne(
  { title: "없는 글" },
  { $set: { author: "새 작성자", views: 0 } },
  { upsert: true }
)
```

### 3.4 Delete -- 문서 삭제

```javascript
// mongosh -- 단일 문서 삭제 (첫 번째 매칭 문서)
db.posts.deleteOne({ author: "홍길동" })

// mongosh -- 여러 문서 삭제
db.posts.deleteMany({ views: { $lt: 1 } })

// mongosh -- 컬렉션 내 모든 문서 삭제
db.posts.deleteMany({})

// mongosh -- 컬렉션 자체를 삭제
db.posts.drop()
```

### 3.5 CRUD 명령어 매핑

```mermaid
flowchart LR
    subgraph RDBMS["RDBMS (SQL)"]
        direction TB
        sql_insert["INSERT INTO posts\nVALUES (...)"]
        sql_select["SELECT * FROM posts\nWHERE author = '홍길동'"]
        sql_update["UPDATE posts\nSET title = '새 제목'\nWHERE id = 1"]
        sql_delete["DELETE FROM posts\nWHERE id = 1"]
    end

    subgraph MongoDB["MongoDB (MQL)"]
        direction TB
        mdb_insert["db.posts.insertOne(\n  { title: '...' }\n)"]
        mdb_select["db.posts.find(\n  { author: '홍길동' }\n)"]
        mdb_update["db.posts.updateOne(\n  { _id: ... },\n  { $set: { title: '새 제목' } }\n)"]
        mdb_delete["db.posts.deleteOne(\n  { _id: ... }\n)"]
    end

    sql_insert <-->|"CREATE"| mdb_insert
    sql_select <-->|"READ"| mdb_select
    sql_update <-->|"UPDATE"| mdb_update
    sql_delete <-->|"DELETE"| mdb_delete

    style RDBMS fill:#0984e3,stroke:#74b9ff,color:#fff
    style MongoDB fill:#e17055,stroke:#fab1a0,color:#fff
    style sql_insert fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style sql_select fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style sql_update fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style sql_delete fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style mdb_insert fill:#fab1a0,stroke:#e17055,color:#2d3436
    style mdb_select fill:#fab1a0,stroke:#e17055,color:#2d3436
    style mdb_update fill:#fab1a0,stroke:#e17055,color:#2d3436
    style mdb_delete fill:#fab1a0,stroke:#e17055,color:#2d3436
```

> **핵심 포인트:** MongoDB의 CRUD 메서드는 `One`과 `Many` 두 변형으로 나뉩니다. `updateOne`은 첫 번째 매칭 문서 하나만, `updateMany`는 조건에 매칭되는 모든 문서를 처리합니다. 실수로 `deleteMany({})`를 실행하면 컬렉션의 모든 문서가 삭제되므로 주의가 필요합니다.

---

## 4. PyMongo -- Python에서 MongoDB 사용

### 4.1 설치와 연결

```bash
# PyMongo 설치
pip install pymongo
```

### 4.2 PyMongo 작업 흐름

```mermaid
flowchart TB
    A["MongoClient 생성\n(연결 설정)"]
    B["Database 선택\nclient['tutorial_db']"]
    C["Collection 선택\ndb['posts']"]
    D{작업 유형}
    E["insert_one / insert_many\n문서 삽입"]
    F["find / find_one\n문서 조회"]
    G["update_one / update_many\n문서 수정"]
    H["delete_one / delete_many\n문서 삭제"]
    I["결과 처리\n(InsertResult / Cursor / UpdateResult)"]
    J["client.close()\n연결 종료"]

    A --> B --> C --> D
    D -->|"Create"| E
    D -->|"Read"| F
    D -->|"Update"| G
    D -->|"Delete"| H
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style C fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#55efc4,stroke:#00b894,color:#2d3436
    style F fill:#0984e3,stroke:#74b9ff,color:#fff
    style G fill:#e17055,stroke:#fab1a0,color:#fff
    style H fill:#fd79a8,stroke:#e84393,color:#fff
    style I fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style J fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 4.3 Python dict와 MongoDB Document 매핑

PyMongo는 Python의 `dict` 타입을 그대로 MongoDB 문서로 사용합니다. 특별한 변환 없이 Python 딕셔너리를 삽입하면 MongoDB 문서가 되고, 조회 결과도 딕셔너리로 돌아옵니다.

| Python 타입 | MongoDB BSON 타입 |
|-------------|-------------------|
| `dict` | Document (Object) |
| `list` | Array |
| `str` | String |
| `int` | Int32 / Int64 |
| `float` | Double |
| `bool` | Boolean |
| `None` | Null |
| `datetime` | Date |
| `bson.ObjectId` | ObjectId |
| `bytes` | Binary |

### 4.4 전체 CRUD 코드 예제

```python
# pymongo_basics.py -- PyMongo 기본 CRUD
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from datetime import datetime

# ── 연결 ──
client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["tutorial_db"]
posts = db["posts"]

# ── Create: 단일 문서 삽입 ──
post = {
    "title": "MongoDB 첫 글",
    "content": "문서 지향 DB의 세계에 오신 것을 환영합니다",
    "author": "홍길동",
    "tags": ["mongodb", "nosql", "tutorial"],
    "views": 0,
    "created_at": datetime.now(),
    "comments": []
}
result = posts.insert_one(post)
print(f"삽입된 문서 ID: {result.inserted_id}")

# ── Create: 여러 문서 삽입 ──
many_result = posts.insert_many([
    {"title": "두 번째 글", "author": "김철수", "tags": ["python"], "views": 10, "created_at": datetime.now()},
    {"title": "세 번째 글", "author": "이영희", "tags": ["database", "nosql"], "views": 5, "created_at": datetime.now()},
])
print(f"삽입된 문서 수: {len(many_result.inserted_ids)}")

# ── Read: 단일 문서 조회 ──
found = posts.find_one({"author": "홍길동"})
if found:
    print(f"조회된 문서: {found['title']}")

# ── Read: 조건과 정렬을 활용한 다중 조회 ──
all_posts = posts.find(
    {"tags": "mongodb"},          # 필터: tags 배열에 "mongodb" 포함
    {"title": 1, "author": 1}     # 프로젝션: title, author만 반환
).sort("created_at", DESCENDING).limit(10)

for p in all_posts:
    print(f"  - {p['title']} by {p['author']}")

# ── Read: 복합 조건 ──
high_view_posts = posts.find({
    "views": {"$gt": 5},
    "author": {"$in": ["홍길동", "김철수"]}
})

# ── Update: 단일 문서 수정 ──
update_result = posts.update_one(
    {"_id": result.inserted_id},
    {
        "$set": {"title": "수정된 제목"},
        "$push": {"tags": "updated"},
        "$inc": {"views": 1}
    }
)
print(f"수정된 문서 수: {update_result.modified_count}")

# ── Update: 여러 문서 수정 ──
posts.update_many(
    {"views": {"$lt": 5}},
    {"$set": {"status": "low_traffic"}}
)

# ── Update: upsert (없으면 삽입) ──
posts.update_one(
    {"title": "존재하지 않는 글"},
    {"$set": {"author": "자동생성", "views": 0, "created_at": datetime.now()}},
    upsert=True
)

# ── Delete: 단일 문서 삭제 ──
delete_result = posts.delete_one({"_id": result.inserted_id})
print(f"삭제된 문서 수: {delete_result.deleted_count}")

# ── Delete: 여러 문서 삭제 ──
posts.delete_many({"status": "low_traffic"})

# ── 연결 종료 ──
client.close()
```

> **핵심 포인트:** PyMongo의 `find()`는 Cursor 객체를 반환합니다. Cursor는 이터레이터이므로 `list(cursor)`로 한 번에 가져오거나 `for` 루프로 순회해야 합니다. 메모리 효율을 위해 대용량 데이터는 반드시 `limit()`을 함께 사용하십시오.

---

## 5. 인덱싱과 집계

### 5.1 인덱스 (Index)

인덱스는 데이터베이스 조회 성능을 극적으로 향상시키는 핵심 기능입니다. 인덱스가 없는 조회는 컬렉션의 모든 문서를 순서대로 검색하는 **풀 스캔(Collection Scan)**을 수행합니다. 책에서 특정 단어를 찾을 때 처음부터 끝까지 읽는 것과 같습니다. 인덱스는 책 뒷면의 **색인(Index)**처럼, 원하는 데이터의 위치를 빠르게 찾아줍니다.

```python
# index_example.py -- MongoDB 인덱스 생성 예제
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["tutorial_db"]
posts = db["posts"]

# ── 단일 필드 인덱스 ──
posts.create_index([("author", ASCENDING)])

# ── 복합 인덱스 (author 오름차순, created_at 내림차순) ──
posts.create_index([("author", ASCENDING), ("created_at", DESCENDING)])

# ── 유니크 인덱스 ──
db.users.create_index([("email", ASCENDING)], unique=True)

# ── 텍스트 인덱스 (전문 검색) ──
posts.create_index([("title", TEXT), ("content", TEXT)])

# ── 텍스트 검색 쿼리 ──
results = posts.find({"$text": {"$search": "MongoDB 문서"}})

# ── 인덱스 목록 확인 ──
for index in posts.list_indexes():
    print(index)

# ── 인덱스 삭제 ──
posts.drop_index("author_1")

client.close()
```

### 5.2 집계 파이프라인 (Aggregation Pipeline)

집계 파이프라인은 데이터를 여러 단계(Stage)에 걸쳐 변환하고 분석하는 MongoDB의 강력한 기능입니다. 공장의 컨베이어 벨트처럼, 데이터가 각 단계를 통과하며 필터링, 변환, 그룹화됩니다.

```mermaid
flowchart TB
    RAW["원본 Collection\n(모든 문서)"]
    MATCH["$match\n조건 필터링\n(SQL WHERE)"]
    GROUP["$group\n그룹화 및 집계\n(SQL GROUP BY)"]
    SORT["$sort\n정렬\n(SQL ORDER BY)"]
    LIMIT["$limit\n결과 개수 제한\n(SQL LIMIT)"]
    PROJECT["$project\n필드 선택/변환\n(SQL SELECT)"]
    RESULT["최종 결과"]

    RAW --> MATCH --> GROUP --> SORT --> LIMIT --> PROJECT --> RESULT

    style RAW fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style MATCH fill:#0984e3,stroke:#74b9ff,color:#fff
    style GROUP fill:#e17055,stroke:#fab1a0,color:#fff
    style SORT fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style LIMIT fill:#fd79a8,stroke:#e84393,color:#fff
    style PROJECT fill:#55efc4,stroke:#00b894,color:#2d3436
    style RESULT fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

주요 집계 연산자는 다음과 같습니다.

| 연산자 | SQL 대응 | 설명 |
|--------|----------|------|
| `$match` | `WHERE` | 조건에 맞는 문서 필터링 |
| `$group` | `GROUP BY` | 필드 기준으로 그룹화, 집계 |
| `$sort` | `ORDER BY` | 결과 정렬 |
| `$limit` | `LIMIT` | 결과 개수 제한 |
| `$skip` | `OFFSET` | 결과 건너뛰기 |
| `$project` | `SELECT` | 반환 필드 선택 및 변환 |
| `$lookup` | `JOIN` | 다른 컬렉션과 조인 |
| `$unwind` | - | 배열 필드를 개별 문서로 펼치기 |
| `$sum` | `SUM()` | 합계 |
| `$avg` | `AVG()` | 평균 |
| `$count` | `COUNT()` | 개수 |

```python
# aggregation_example.py -- Aggregation Pipeline 예제
from pymongo import MongoClient

client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["tutorial_db"]
posts = db["posts"]

# ── 예제 1: 태그별 게시글 수 집계 ──
tag_count_pipeline = [
    # 1단계: tags 배열을 개별 요소로 펼치기
    {"$unwind": "$tags"},
    # 2단계: 태그별로 그룹화하여 개수 집계
    {"$group": {
        "_id": "$tags",
        "count": {"$sum": 1},
        "avg_views": {"$avg": "$views"}
    }},
    # 3단계: 개수 내림차순 정렬
    {"$sort": {"count": -1}},
    # 4단계: 상위 10개만 반환
    {"$limit": 10},
    # 5단계: 필드 이름 정리
    {"$project": {
        "_id": 0,
        "tag": "$_id",
        "count": 1,
        "avg_views": {"$round": ["$avg_views", 1]}
    }}
]

print("=== 태그별 게시글 통계 ===")
for result in posts.aggregate(tag_count_pipeline):
    print(f"  #{result['tag']}: {result['count']}개 (평균 조회수: {result['avg_views']})")

# ── 예제 2: $lookup으로 사용자 정보 조인 ──
posts_with_user_pipeline = [
    {"$match": {"views": {"$gt": 0}}},
    {"$lookup": {
        "from": "users",           # 조인할 컬렉션
        "localField": "author_id", # posts의 조인 키
        "foreignField": "_id",     # users의 조인 키
        "as": "author_info"        # 결과를 담을 배열 필드명
    }},
    {"$unwind": "$author_info"},
    {"$project": {
        "title": 1,
        "views": 1,
        "author_name": "$author_info.name",
        "author_email": "$author_info.email"
    }}
]

client.close()
```

> **핵심 포인트:** Aggregation Pipeline의 각 단계는 이전 단계의 출력을 입력으로 받습니다. `$match`를 파이프라인의 가능한 한 앞에 배치해야 처리 문서 수를 줄여 성능을 향상시킬 수 있습니다. 특히 `$match`가 인덱스 필드를 사용하면 효과가 극대화됩니다.

---

## 6. 스키마 설계 -- Embedding vs Referencing

### 6.1 스키마 설계의 핵심 질문

MongoDB가 "스키마리스(Schemaless)"라고 해서 설계가 필요 없다는 의미는 아닙니다. 오히려 **어떻게 데이터를 구조화할 것인가**에 대한 의사결정이 더욱 중요합니다. MongoDB 스키마 설계의 핵심은 **"관계 데이터를 어떻게 표현할 것인가"**입니다.

실생활 비유를 들어 보겠습니다. 취업 지원 서류를 준비할 때, 경력사항을 처리하는 두 가지 방법이 있습니다.

- **이력서에 직접 기재 (Embedding):** 이력서 한 장 안에 모든 경력사항을 상세히 작성합니다. 한 장만 제출하면 되고, 면접관이 모든 정보를 한 번에 볼 수 있습니다.
- **별도 경력증명서 첨부 (Referencing):** 이력서에는 "별첨 경력증명서 참조"라고만 쓰고, 경력증명서를 별도 문서로 첨부합니다. 경력증명서는 다른 지원서에도 재사용할 수 있습니다.

### 6.2 Embedding (내장 문서)

Embedding은 관련 데이터를 하나의 문서 안에 **중첩된 형태로 포함**시키는 방식입니다.

```json
// Embedding 예시: 댓글을 게시글 문서 안에 내장
{
  "_id": "ObjectId('...')",
  "title": "MongoDB 스키마 설계",
  "author": "홍길동",
  "content": "Embedding과 Referencing을 알아봅시다",
  "comments": [
    {
      "user": "김철수",
      "text": "좋은 글이네요!",
      "created_at": "2024-01-15T09:00:00"
    },
    {
      "user": "이영희",
      "text": "참고가 됩니다.",
      "created_at": "2024-01-15T10:00:00"
    }
  ]
}
```

| 항목 | 내용 |
|------|------|
| 장점 | 단일 쿼리로 모든 관련 데이터 조회 가능 |
| 장점 | `JOIN` 연산 불필요, 높은 읽기 성능 |
| 장점 | 원자적(Atomic) 업데이트 보장 |
| 단점 | 문서 크기 제한 16MB 초과 불가 |
| 단점 | 내장 데이터가 많이 변경되면 전체 문서 업데이트 필요 |
| 단점 | 내장 데이터를 독립적으로 조회하기 어려움 |
| 단점 | 동일 데이터가 여러 문서에 중복될 수 있음 |
| 적합한 관계 | 1:1, 1:Few (1:소수) |
| 적합한 경우 | 데이터가 항상 함께 조회되는 경우 |

### 6.3 Referencing (참조)

Referencing은 관계형 데이터베이스의 외래 키(Foreign Key)처럼, 다른 문서의 `_id`를 저장하여 **참조 관계**를 표현하는 방식입니다.

```json
// Referencing 예시: 댓글을 별도 컬렉션으로 분리
// posts 컬렉션
{
  "_id": "ObjectId('post_001')",
  "title": "MongoDB 스키마 설계",
  "author_id": "ObjectId('user_001')",
  "content": "Embedding과 Referencing을 알아봅시다"
}

// comments 컬렉션
{
  "_id": "ObjectId('comment_001')",
  "post_id": "ObjectId('post_001')",
  "user_id": "ObjectId('user_002')",
  "text": "좋은 글이네요!",
  "created_at": "2024-01-15T09:00:00"
}
```

| 항목 | 내용 |
|------|------|
| 장점 | 데이터 정규화, 중복 최소화 |
| 장점 | 각 컬렉션을 독립적으로 업데이트 가능 |
| 장점 | 문서 크기 제한 문제 없음 |
| 장점 | 참조 데이터를 다양한 컨텍스트에서 재사용 가능 |
| 단점 | 관련 데이터 조회 시 `$lookup` 또는 추가 쿼리 필요 |
| 단점 | 애플리케이션 수준의 조인 처리 필요 |
| 단점 | 원자적 트랜잭션 처리가 복잡 |
| 적합한 관계 | 1:Many (1:다수), M:N (다:다) |
| 적합한 경우 | 참조 데이터가 자주 변경되거나 독립적으로 조회되는 경우 |

### 6.4 Embedding vs Referencing 비교 테이블

| 비교 기준 | Embedding | Referencing |
|-----------|-----------|-------------|
| 쿼리 횟수 | 1회 | 2회 이상 |
| 읽기 성능 | 매우 빠름 | 상대적으로 느림 |
| 쓰기 성능 | 데이터 크기에 따라 느려질 수 있음 | 빠름 |
| 데이터 중복 | 가능성 있음 | 없음 (정규화) |
| 문서 크기 | 무한정 커질 수 있음 | 작고 일정함 |
| 관계 유형 | 1:1, 1:Few | 1:Many, M:N |
| 데이터 변경 빈도 | 낮음 | 높음 |
| 독립적 접근 필요 | 없음 | 있음 |

### 6.5 스키마 설계 결정 플로우차트

```mermaid
flowchart LR
    START["설계 시작"] --> Q1{"함께 조회?"}
    Q1 -->|"No"| REF["Referencing"]
    Q1 -->|"Yes"| Q2{"16MB 이하?"}
    Q2 -->|"No"| REF
    Q2 -->|"Yes"| Q3{"자주 변경?"}
    Q3 -->|"No"| EMBED["Embedding"]
    Q3 -->|"Yes"| Q4{"N이 수천 이상?"}
    Q4 -->|"Yes"| REF
    Q4 -->|"No"| Q5{"공유 데이터?"}
    Q5 -->|"Yes"| REF
    Q5 -->|"No"| HYBRID["Hybrid"]

    style START fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style Q1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Q2 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Q3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Q4 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Q5 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style EMBED fill:#55efc4,stroke:#00b894,color:#2d3436
    style REF fill:#e17055,stroke:#fab1a0,color:#fff
    style HYBRID fill:#0984e3,stroke:#74b9ff,color:#fff
```

### 6.6 실전 예제 -- 게시판 스키마 설계 비교

아래는 동일한 게시판 서비스를 Embedding 방식과 Referencing 방식으로 각각 설계한 예시입니다.

**방식 A: Embedding (댓글 수가 적은 경우)**

```python
# schema_embedding.py -- Embedding 방식의 게시판 스키마
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["tutorial_db"]
posts = db["posts_embedded"]

# 게시글 + 댓글을 하나의 문서로 저장
post_doc = {
    "title": "MongoDB 스키마 설계 강의",
    "content": "오늘은 Embedding과 Referencing을 배웁니다.",
    "author": {
        "name": "홍길동",
        "email": "hong@example.com"
    },
    "tags": ["mongodb", "nosql"],
    "views": 0,
    "created_at": datetime.now(),
    # 댓글을 배열로 내장
    "comments": [
        {
            "author": "김철수",
            "text": "매우 유익합니다!",
            "likes": 3,
            "created_at": datetime.now()
        }
    ],
    # 메타데이터도 함께 내장
    "stats": {
        "comment_count": 1,
        "like_count": 0
    }
}

result = posts.insert_one(post_doc)

# 게시글과 댓글을 단 한 번의 쿼리로 조회
full_post = posts.find_one({"_id": result.inserted_id})
print(f"댓글 수: {len(full_post['comments'])}")

# 댓글 추가 ($push 연산자 사용)
posts.update_one(
    {"_id": result.inserted_id},
    {
        "$push": {"comments": {
            "author": "이영희",
            "text": "감사합니다.",
            "likes": 0,
            "created_at": datetime.now()
        }},
        "$inc": {"stats.comment_count": 1}
    }
)

client.close()
```

**방식 B: Referencing (댓글 수가 많거나 독립 접근이 필요한 경우)**

```python
# schema_referencing.py -- Referencing 방식의 게시판 스키마
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["tutorial_db"]
posts = db["posts_ref"]
comments = db["comments"]
users = db["users"]

# 사용자 컬렉션 (독립적으로 관리)
user_result = users.insert_one({
    "name": "홍길동",
    "email": "hong@example.com",
    "role": "author",
    "created_at": datetime.now()
})
user_id = user_result.inserted_id

# 게시글 컬렉션 (author_id로 참조)
post_result = posts.insert_one({
    "title": "MongoDB 스키마 설계 강의",
    "content": "오늘은 Embedding과 Referencing을 배웁니다.",
    "author_id": user_id,  # users 컬렉션의 _id 참조
    "tags": ["mongodb", "nosql"],
    "views": 0,
    "created_at": datetime.now()
})
post_id = post_result.inserted_id

# 댓글 컬렉션 (post_id로 참조)
comments.insert_many([
    {
        "post_id": post_id,       # posts 컬렉션의 _id 참조
        "author_id": user_id,
        "text": "매우 유익합니다!",
        "likes": 3,
        "created_at": datetime.now()
    }
])

# $lookup으로 게시글 + 작성자 + 댓글을 한번에 조회
pipeline = [
    {"$match": {"_id": post_id}},
    {"$lookup": {
        "from": "users",
        "localField": "author_id",
        "foreignField": "_id",
        "as": "author"
    }},
    {"$unwind": "$author"},
    {"$lookup": {
        "from": "comments",
        "localField": "_id",
        "foreignField": "post_id",
        "as": "comments"
    }},
    {"$project": {
        "title": 1,
        "content": 1,
        "author_name": "$author.name",
        "comment_count": {"$size": "$comments"}
    }}
]

result = list(posts.aggregate(pipeline))
if result:
    print(f"제목: {result[0]['title']}, 댓글 수: {result[0]['comment_count']}")

client.close()
```

> **핵심 포인트:** MongoDB 스키마 설계의 황금률은 **"애플리케이션이 데이터에 접근하는 패턴을 기준으로 설계하라"**입니다. 항상 함께 조회되는 데이터는 Embedding으로, 독립적으로 관리되거나 매우 많은 수를 가진 관계 데이터는 Referencing으로 처리합니다.

---

## 7. MongoDB vs RDBMS 실전 비교

### 7.1 동일한 게시판 서비스 구현 비교

같은 게시판 서비스를 SQLite(RDBMS)와 MongoDB로 구현하면 어떻게 달라지는지 비교해 보겠습니다.

```mermaid
flowchart LR
    subgraph RDBMS["SQLite / MySQL 방식"]
        direction TB
        R1["users 테이블\n(id, name, email, role)"]
        R2["posts 테이블\n(id, title, content, user_id)"]
        R3["comments 테이블\n(id, post_id, user_id, text)"]
        R4["tags 테이블\n(id, name)"]
        R5["post_tags 테이블\n(post_id, tag_id)"]
        R1 -->|"FK"| R2
        R2 -->|"FK"| R3
        R2 -->|"M:N"| R5
        R4 -->|"M:N"| R5
    end

    subgraph MongoDB["MongoDB 방식 (Hybrid)"]
        direction TB
        M1["users Collection\n{ _id, name, email }"]
        M2["posts Collection\n{ _id, title, author_id,\ntags: ['...'], comments: [...] }"]
        M3["comments Collection\n(대댓글 또는 대용량인 경우)"]
        M1 -->|"Referencing"| M2
        M2 -->|"Embedding (소량)\nReferencing (대량)"| M3
    end

    style RDBMS fill:#0984e3,stroke:#74b9ff,color:#fff
    style MongoDB fill:#e17055,stroke:#fab1a0,color:#fff
    style R1 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style R2 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style R3 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style R4 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style R5 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style M1 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style M2 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style M3 fill:#fab1a0,stroke:#e17055,color:#2d3436
```

### 7.2 상세 비교 테이블

| 비교 항목 | RDBMS (SQLite/MySQL) | MongoDB |
|-----------|----------------------|---------|
| 스키마 | 사전 정의 필수, 변경 시 마이그레이션 | 유연, 동적 변경 가능 |
| 데이터 모델 | 테이블 + 행 (정형) | 문서 (반정형, 비정형) |
| 쿼리 언어 | SQL (표준화) | MQL (MongoDB 전용) |
| 관계 처리 | JOIN (강력하고 유연) | Embedding 또는 `$lookup` |
| 트랜잭션 | ACID 완전 지원 | v4.0+ Multi-document 트랜잭션 |
| 수평 확장 | 어려움 (샤딩 복잡) | 기본 제공 (샤딩 내장) |
| 조회 성능 | 복잡한 관계 쿼리에 강함 | 단순 문서 조회에 강함 |
| 쓰기 성능 | 상대적으로 낮음 | 높음 (분산 쓰기) |
| 집계/분석 | SQL 집계 함수 | Aggregation Pipeline |
| 전문 검색 | LIKE (제한적) | Text Index |
| 지리 데이터 | 확장 모듈 필요 | GeoJSON 기본 지원 |
| 데이터 일관성 | 강한 일관성 | 설정에 따라 조절 가능 |

### 7.3 언제 MongoDB를 선택하는가

MongoDB가 적합한 상황과 RDBMS가 적합한 상황을 명확히 이해하는 것이 중요합니다.

| MongoDB 선택 기준 | RDBMS 선택 기준 |
|------------------|----------------|
| 데이터 구조가 자주 변경됨 | 데이터 구조가 안정적임 |
| 반정형 / 비정형 데이터 | 정형 데이터 |
| 대용량 수평 확장 필요 | 복잡한 JOIN 쿼리 필요 |
| 빠른 프로토타이핑 | 강력한 트랜잭션 요구 |
| 지리 데이터, 실시간 처리 | 금융, 회계 (강한 ACID) |
| 카탈로그, 콘텐츠 관리 | 정규화된 관계 데이터 |
| IoT 로그, 이벤트 데이터 | 복잡한 관계형 분석 |
| 사용자 맞춤 데이터 | 표준 ERP / CRM 시스템 |

> **핵심 포인트:** MongoDB와 RDBMS는 경쟁 관계가 아닌 **상호 보완 관계**입니다. 실제 현업에서는 두 가지를 함께 사용하는 경우가 많습니다. 예를 들어 사용자 계정과 결제 정보는 PostgreSQL에, 상품 카탈로그와 사용자 활동 로그는 MongoDB에 저장하는 방식으로 각 DB의 강점을 활용합니다.

---

## 8. 핵심 정리

### 8.1 MongoDB CRUD 명령어 요약

| 작업 | mongosh (MQL) | PyMongo 메서드 | 반환 값 |
|------|--------------|----------------|---------|
| 단일 삽입 | `db.col.insertOne({})` | `col.insert_one({})` | `InsertOneResult` |
| 다중 삽입 | `db.col.insertMany([])` | `col.insert_many([])` | `InsertManyResult` |
| 단일 조회 | `db.col.findOne({})` | `col.find_one({})` | `dict` 또는 `None` |
| 다중 조회 | `db.col.find({})` | `col.find({})` | `Cursor` |
| 단일 수정 | `db.col.updateOne({}, {})` | `col.update_one({}, {})` | `UpdateResult` |
| 다중 수정 | `db.col.updateMany({}, {})` | `col.update_many({}, {})` | `UpdateResult` |
| 단일 삭제 | `db.col.deleteOne({})` | `col.delete_one({})` | `DeleteResult` |
| 다중 삭제 | `db.col.deleteMany({})` | `col.delete_many({})` | `DeleteResult` |
| 문서 수 | `db.col.countDocuments({})` | `col.count_documents({})` | `int` |
| 집계 | `db.col.aggregate([])` | `col.aggregate([])` | `CommandCursor` |

### 8.2 스키마 설계 가이드 요약

| 상황 | 권장 방식 | 이유 |
|------|-----------|------|
| 1:1 관계 | Embedding | 항상 함께 조회, 단순함 |
| 1:Few (1:소수) | Embedding | 배열 크기가 예측 가능 |
| 1:Many (1:다수, 수백~수천) | Referencing | 문서 크기 초과 방지 |
| 1:Squillions (수백만+) | Referencing | 반드시 분리 |
| M:N 관계 | Referencing | 데이터 중복 방지 |
| 자주 변경되는 내장 데이터 | Referencing | 업데이트 비용 절감 |
| 항상 함께 읽는 데이터 | Embedding | 쿼리 횟수 최소화 |
| 독립적으로 접근하는 데이터 | Referencing | 유연한 조회 가능 |

### 8.3 핵심 요약

| 개념 | 핵심 내용 |
|------|-----------|
| MongoDB | 문서 지향 NoSQL DB, BSON 형식, 유연한 스키마 |
| Collection | RDBMS의 Table에 해당하는 문서의 모음 |
| Document | JSON/BSON 형식의 데이터 단위, `_id` 필드 필수 |
| ObjectId | 12바이트 자동 생성 고유 식별자 |
| PyMongo | Python에서 MongoDB를 사용하는 공식 드라이버 |
| 인덱스 | 조회 성능 향상, 단일/복합/텍스트 인덱스 |
| Aggregation | 다단계 데이터 변환 파이프라인 (`$match`, `$group` 등) |
| Embedding | 관련 데이터를 문서 내부에 내장 (1:1, 1:Few) |
| Referencing | `_id`를 통한 참조 관계 (1:Many, M:N) |
| $lookup | 다른 컬렉션과의 조인 (Aggregation Pipeline 단계) |

### 8.4 다음 강의 미리보기

다음 강의에서는 **벡터 데이터베이스(Vector Database)**를 다룹니다. AI 시대의 핵심 인프라인 벡터 DB가 기존 데이터베이스와 어떻게 다른지, 그리고 텍스트/이미지 유사도 검색이 어떻게 작동하는지 살펴봅니다. MongoDB Atlas Vector Search와 전용 벡터 DB(Pinecone, Chroma, Milvus)의 차이점도 함께 비교합니다.

---

> **이전 강의:** [NoSQL과 CAP 정리](09_nosql_and_cap_theorem.md)
>
> **다음 강의:** [벡터 데이터베이스의 이해](11_vector_databases.md)
