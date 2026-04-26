# 벡터 데이터베이스 구현체 실습 비교

> ChromaDB, FAISS, pgvector — 세 가지 대표 구현체를 직접 실습하며 각각의 특성과 적합한 사용 시나리오를 체계적으로 비교합니다

---

## 1. 벡터 데이터베이스 구현체 비교

### 구현체의 세 가지 유형

벡터 검색 기능을 제공하는 도구는 크게 세 가지 유형으로 분류됩니다. 각 유형은 설계 철학과 목적이 근본적으로 다릅니다.

**실생활 비유:** 음식을 저장하고 꺼내는 방법에 빗대어 생각해 보겠습니다. 전용 냉장고(전용 벡터 DB)는 식품 보관에 최적화된 설계로 편의성이 높습니다. 아이스박스(라이브러리)는 직접 얼음을 채워 써야 하지만 가볍고 어디서나 사용 가능합니다. 기존 냉장고에 추가하는 야채칸 확장 서랍(Extension)은 기존 인프라를 그대로 활용하면서 기능만 추가하는 방식입니다.

| 유형 | 대표 구현체 | 특징 | 주요 대상 |
|------|-------------|------|-----------|
| 전용 벡터 DB | ChromaDB, Pinecone, Weaviate | 벡터 검색에 최적화된 독립 시스템 | LLM 앱, RAG 파이프라인 |
| 라이브러리 | FAISS, Annoy, ScaNN | 애플리케이션 내장형 인덱스 | 연구, 고성능 검색 엔진 |
| DB 확장(Extension) | pgvector, sqlite-vss | 기존 RDBMS에 벡터 기능 추가 | 기존 SQL 인프라 보유 팀 |

### ChromaDB, FAISS, pgvector 개요

이번 강의에서 실습할 세 가지 구현체를 개괄적으로 살펴보겠습니다.

| 항목 | ChromaDB | FAISS | pgvector |
|------|----------|-------|----------|
| 유형 | 전용 벡터 DB | 벡터 검색 라이브러리 | PostgreSQL 확장 |
| 개발사 | Chroma (오픈소스) | Meta AI Research | PostgreSQL 커뮤니티 |
| 설치 난이도 | 낮음 (pip 한 줄) | 낮음 (pip 한 줄) | 중간 (DB 서버 필요) |
| 영속성 | 선택 가능 (인메모리/파일) | 별도 직렬화 필요 | 기본 지원 (PostgreSQL) |
| 메타데이터 필터링 | 기본 내장 | 미지원 (별도 구현) | SQL WHERE 절 활용 |
| 확장성 | 중간 | 매우 높음 (GPU 가속) | 중간~높음 |
| 트랜잭션 지원 | 미지원 | 미지원 | 완전 지원 (ACID) |
| 적합 사례 | 빠른 프로토타입, RAG | 대규모 벡터 검색 | SQL과 벡터 검색 통합 |

```mermaid
flowchart TB
    ROOT["벡터 DB 구현체"]
    TYPE1["전용 벡터 DB"]
    TYPE2["벡터 검색 라이브러리"]
    TYPE3["DB 확장(Extension)"]
    CHROMA["ChromaDB\n오픈소스, Python 네이티브"]
    PINE["Pinecone\n클라우드 매니지드"]
    WEAV["Weaviate\n멀티모달 지원"]
    FAISS["FAISS\nMeta AI Research"]
    ANNOY["Annoy\nSpotify"]
    SCANN["ScaNN\nGoogle"]
    PGV["pgvector\nPostgreSQL 확장"]
    SQVSS["sqlite-vss\nSQLite 확장"]

    ROOT --> TYPE1
    ROOT --> TYPE2
    ROOT --> TYPE3
    TYPE1 --> CHROMA
    TYPE1 --> PINE
    TYPE1 --> WEAV
    TYPE2 --> FAISS
    TYPE2 --> ANNOY
    TYPE2 --> SCANN
    TYPE3 --> PGV
    TYPE3 --> SQVSS

    style ROOT fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style TYPE1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style TYPE2 fill:#e17055,stroke:#fab1a0,color:#fff
    style TYPE3 fill:#00b894,stroke:#55efc4,color:#fff
    style CHROMA fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style PINE fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style WEAV fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style FAISS fill:#fab1a0,stroke:#e17055,color:#2d3436
    style ANNOY fill:#fab1a0,stroke:#e17055,color:#2d3436
    style SCANN fill:#fab1a0,stroke:#e17055,color:#2d3436
    style PGV fill:#55efc4,stroke:#00b894,color:#2d3436
    style SQVSS fill:#55efc4,stroke:#00b894,color:#2d3436
```

> **핵심 포인트:** 세 유형은 설계 목적이 다르므로 우열을 가릴 수 없습니다. 팀의 인프라 환경, 데이터 규모, 기능 요구사항에 따라 가장 적합한 도구를 선택하는 것이 중요합니다.

---

## 2. ChromaDB 실습

### ChromaDB 소개

ChromaDB는 LLM 애플리케이션을 위해 설계된 오픈소스 벡터 데이터베이스입니다. Python 네이티브로 동작하며, 복잡한 설정 없이 몇 줄의 코드만으로 벡터 저장과 검색을 시작할 수 있습니다.

**실생활 비유:** ChromaDB는 도서관의 사서와 같습니다. 책(문서)을 건네주면 사서가 직접 분류하고(임베딩), 원하는 주제의 책을 찾아달라고 요청하면 관련 있는 책들을 꺼내줍니다(유사도 검색). 이용자는 분류 체계의 내부 동작 방식을 몰라도 됩니다.

**주요 특징:**
- 설치: `pip install chromadb` 한 줄로 완료
- 자동 임베딩: 텍스트를 직접 넣으면 내부에서 임베딩 처리
- 인메모리 / 영속 저장 선택 가능
- 메타데이터 필터링 기본 내장
- LangChain, LlamaIndex 등 주요 LLM 프레임워크와 통합 지원

### Collection 개념

ChromaDB에서 **Collection**은 관계형 데이터베이스의 테이블에 해당하는 개념입니다. 하나의 Collection에는 문서, 임베딩, 메타데이터, ID가 함께 저장됩니다.

| ChromaDB 개념 | RDBMS 대응 개념 | 설명 |
|---------------|----------------|------|
| Client | 데이터베이스 연결 | 서버 또는 인메모리 인스턴스 |
| Collection | 테이블 | 문서와 임베딩을 묶은 단위 |
| Document | 행(Row) | 원본 텍스트 |
| Embedding | 열(Column) | 벡터 표현 (자동 생성 가능) |
| Metadata | 열(Column) | 필터링용 부가 정보 |
| ID | Primary Key | 각 문서의 고유 식별자 |

### ChromaDB 워크플로우

```mermaid
flowchart TB
    INST["pip install chromadb"]
    CLIENT["Client 생성\n인메모리 or 영속"]
    COLL["Collection 생성\nhnsw:space 지정"]
    ADD["문서 추가\ndocuments + metadata + ids"]
    EMBED["자동 임베딩\n(내부 처리)"]
    QUERY["쿼리 실행\nquery_texts"]
    FILTER["메타데이터 필터\nwhere 조건"]
    RESULT["결과 반환\ndocuments + distances"]

    INST --> CLIENT
    CLIENT --> COLL
    COLL --> ADD
    ADD --> EMBED
    EMBED --> QUERY
    QUERY --> FILTER
    FILTER --> RESULT

    style INST fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style CLIENT fill:#0984e3,stroke:#74b9ff,color:#fff
    style COLL fill:#0984e3,stroke:#74b9ff,color:#fff
    style ADD fill:#e17055,stroke:#fab1a0,color:#fff
    style EMBED fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style QUERY fill:#e17055,stroke:#fab1a0,color:#fff
    style FILTER fill:#fd79a8,stroke:#e84393,color:#fff
    style RESULT fill:#00b894,stroke:#55efc4,color:#fff
```

### ChromaDB 코드 예제

```python
# chromadb_example.py -- ChromaDB 기본 사용법
import chromadb

# ── 클라이언트 생성 ──
client = chromadb.Client()  # 인메모리
# client = chromadb.PersistentClient(path="./chroma_db")  # 영속 저장

# ── 컬렉션 생성 ──
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# ── 문서 추가 (자동 임베딩) ──
collection.add(
    documents=[
        "Python은 배우기 쉬운 프로그래밍 언어입니다",
        "JavaScript는 웹 브라우저에서 실행되는 언어입니다",
        "SQL은 데이터베이스를 조작하는 언어입니다",
        "오늘 서울의 날씨는 맑고 따뜻합니다",
        "머신러닝은 데이터에서 패턴을 학습하는 AI 기술입니다",
    ],
    metadatas=[
        {"category": "programming", "level": "beginner"},
        {"category": "programming", "level": "intermediate"},
        {"category": "database", "level": "beginner"},
        {"category": "weather", "level": "none"},
        {"category": "ai", "level": "advanced"},
    ],
    ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
)

# ── 유사도 검색 ──
results = collection.query(
    query_texts=["프로그래밍 언어를 배우고 싶어요"],
    n_results=3
)
print("검색 결과:", results["documents"])

# ── 메타데이터 필터링 + 검색 ──
results = collection.query(
    query_texts=["코딩 입문"],
    n_results=2,
    where={"category": "programming"}
)
```

### ChromaDB 고급 기능

ChromaDB는 기본 사용법 외에도 실전 운용을 위한 다양한 고급 기능을 제공합니다.

```python
# chromadb_advanced.py -- ChromaDB 고급 기능
import chromadb
from chromadb.utils import embedding_functions

# ── 커스텀 임베딩 함수 사용 ──
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_API_KEY",
    model_name="text-embedding-3-small"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="custom_embeddings",
    embedding_function=openai_ef
)

# ── 문서 업데이트 ──
collection.update(
    ids=["doc1"],
    documents=["Python은 범용 프로그래밍 언어입니다 (갱신됨)"],
    metadatas=[{"category": "programming", "level": "beginner", "updated": True}]
)

# ── 문서 삭제 ──
collection.delete(ids=["doc4"])

# ── 컬렉션 통계 확인 ──
print(f"문서 수: {collection.count()}")
```

### ChromaDB 메타데이터 필터 연산자

ChromaDB는 다양한 조건 연산자를 지원하여 복합 필터링이 가능합니다.

| 연산자 | 의미 | 예시 |
|--------|------|------|
| `$eq` | 같음 (기본값) | `{"category": {"$eq": "programming"}}` |
| `$ne` | 같지 않음 | `{"level": {"$ne": "beginner"}}` |
| `$in` | 목록 중 하나 | `{"category": {"$in": ["programming", "ai"]}}` |
| `$nin` | 목록에 없음 | `{"level": {"$nin": ["none"]}}` |
| `$and` | AND 조건 | `{"$and": [{"category": "programming"}, {"level": "beginner"}]}` |
| `$or` | OR 조건 | `{"$or": [{"category": "ai"}, {"category": "database"}]}` |

```python
# chromadb_filter_examples.py -- ChromaDB 복합 필터링 예제
import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

# ── AND 조건 필터 ──
results = collection.query(
    query_texts=["머신러닝 입문"],
    n_results=3,
    where={
        "$and": [
            {"category": {"$in": ["ai", "programming"]}},
            {"level": {"$ne": "none"}}
        ]
    }
)

# ── 결과 상세 조회 옵션 ──
results = collection.query(
    query_texts=["데이터베이스"],
    n_results=2,
    include=["documents", "metadatas", "distances", "embeddings"]
)
print("거리:", results["distances"])
print("메타데이터:", results["metadatas"])
```

> **핵심 포인트:** ChromaDB는 자동 임베딩 기능 덕분에 텍스트를 직접 넣는 것만으로 벡터 검색이 동작합니다. 프로토타입과 소규모 RAG 파이프라인에 가장 빠르게 도입할 수 있는 선택지입니다.

---

## 3. FAISS 실습

### FAISS 소개

FAISS(Facebook AI Similarity Search)는 Meta AI Research에서 개발한 고성능 벡터 유사도 검색 라이브러리입니다. 수십억 개의 벡터를 대상으로 초고속 검색이 가능하며, GPU 가속을 지원합니다.

**실생활 비유:** FAISS는 창고 물류 시스템의 고속 분류 컨베이어 벨트와 같습니다. 물건(벡터)을 빠르게 분류하고 찾아낼 수 있지만, 물건에 부착된 라벨(메타데이터)은 별도의 대장(외부 DB)에 기록해야 합니다. 순수하게 "빠른 탐색"에만 집중한 도구입니다.

**주요 특징:**
- 설치: `pip install faiss-cpu` (GPU 버전은 `faiss-gpu`)
- 메타데이터 관리: 미지원 — 별도로 구현 필요
- 여러 인덱스 타입 제공: 정확도 vs 속도 트레이드오프 선택 가능
- 대규모 데이터(수억~수십억 벡터)에서 검증된 성능
- 연구 환경 및 프로덕션 추천 검색 엔진에서 널리 사용

### FAISS 인덱스 타입 비교

```mermaid
flowchart TB
    FAISS["FAISS 인덱스 타입"]
    FLAT["IndexFlatL2 / IndexFlatIP\n정확한 완전 탐색(Brute Force)"]
    IVF["IndexIVFFlat\nIVF 기반 근사 검색\n클러스터로 나눠 탐색 범위 제한"]
    HNSW["IndexHNSWFlat\nHNSW 알고리즘\n그래프 기반 근사 검색"]
    PQ["IndexIVFPQ\nProduct Quantization\n메모리 압축 + 근사 검색"]

    FLAT_PROS["장점: 완벽한 정확도\n단점: 느린 속도, 대용량 불가"]
    IVF_PROS["장점: nlist 조정으로 속도/정확도 균형\n단점: 학습(train) 단계 필요"]
    HNSW_PROS["장점: 빠른 검색, 학습 불필요\n단점: 높은 메모리 사용"]
    PQ_PROS["장점: 최소 메모리, 대용량 가능\n단점: 정확도 다소 저하"]

    FAISS --> FLAT
    FAISS --> IVF
    FAISS --> HNSW
    FAISS --> PQ
    FLAT --> FLAT_PROS
    IVF --> IVF_PROS
    HNSW --> HNSW_PROS
    PQ --> PQ_PROS

    style FAISS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style FLAT fill:#0984e3,stroke:#74b9ff,color:#fff
    style IVF fill:#e17055,stroke:#fab1a0,color:#fff
    style HNSW fill:#00b894,stroke:#55efc4,color:#fff
    style PQ fill:#fd79a8,stroke:#e84393,color:#fff
    style FLAT_PROS fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style IVF_PROS fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style HNSW_PROS fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style PQ_PROS fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

| 인덱스 타입 | 탐색 방식 | 속도 | 정확도 | 메모리 | 학습 필요 |
|-------------|-----------|------|--------|--------|-----------|
| IndexFlatL2 | 완전 탐색 | 느림 | 100% | 높음 | 불필요 |
| IndexIVFFlat | 클러스터 기반 | 빠름 | 높음 | 중간 | 필요 |
| IndexHNSWFlat | 그래프 탐색 | 매우 빠름 | 높음 | 높음 | 불필요 |
| IndexIVFPQ | 압축 + 클러스터 | 매우 빠름 | 중간 | 낮음 | 필요 |

### FAISS 코드 예제

```python
# faiss_example.py -- FAISS 벡터 검색
import faiss
import numpy as np

# ── 임베딩 데이터 준비 (임의 벡터) ──
dimension = 384
num_vectors = 1000
vectors = np.random.random((num_vectors, dimension)).astype('float32')
query = np.random.random((1, dimension)).astype('float32')

# ── IndexFlatL2 (정확한 검색) ──
index_flat = faiss.IndexFlatL2(dimension)
index_flat.add(vectors)
distances, indices = index_flat.search(query, k=5)
print(f"Flat 검색 결과: {indices[0]}, 거리: {distances[0]}")

# ── IndexIVFFlat (근사 검색, 더 빠름) ──
nlist = 10  # 클러스터 수
quantizer = faiss.IndexFlatL2(dimension)
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index_ivf.train(vectors)  # 학습 필요
index_ivf.add(vectors)
index_ivf.nprobe = 3  # 탐색할 클러스터 수
distances, indices = index_ivf.search(query, k=5)

# ── 인덱스 저장/로드 ──
faiss.write_index(index_flat, "vectors.index")
loaded_index = faiss.read_index("vectors.index")
```

### FAISS 메타데이터 관리 패턴

FAISS는 메타데이터를 직접 저장하지 않으므로, 외부 저장소와 함께 사용하는 패턴이 일반적입니다.

```python
# faiss_with_metadata.py -- FAISS + 외부 메타데이터 관리
import faiss
import numpy as np
import json

# ── 외부 메타데이터 저장 (Python dict 또는 SQLite) ──
metadata_store = {}

def add_vectors_with_metadata(index, vectors, metadatas):
    start_id = index.ntotal
    index.add(vectors)
    for i, meta in enumerate(metadatas):
        metadata_store[start_id + i] = meta
    return start_id

def search_with_metadata(index, query, k=5):
    distances, indices = index.search(query, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "distance": float(dist),
            "metadata": metadata_store.get(int(idx), {})
        })
    return results

# ── 사용 예시 ──
dimension = 384
index = faiss.IndexFlatL2(dimension)

sample_vectors = np.random.random((3, dimension)).astype('float32')
sample_metadata = [
    {"text": "Python 가이드", "category": "programming"},
    {"text": "SQL 입문", "category": "database"},
    {"text": "딥러닝 개요", "category": "ai"},
]
add_vectors_with_metadata(index, sample_vectors, sample_metadata)

query = np.random.random((1, dimension)).astype('float32')
results = search_with_metadata(index, query, k=2)
print(results)
```

### FAISS 실전 활용: GPU 가속 및 배치 검색

대규모 프로덕션 환경에서는 GPU 가속을 활용하거나 배치 쿼리로 처리량을 높이는 것이 중요합니다.

```python
# faiss_production.py -- FAISS 실전 활용 패턴
import faiss
import numpy as np

dimension = 384
num_vectors = 5_000_000  # 500만 벡터

# ── GPU 가속 (faiss-gpu 설치 필요) ──
# res = faiss.StandardGpuResources()
# index_flat = faiss.IndexFlatL2(dimension)
# gpu_index = faiss.index_cpu_to_gpu(res, 0, index_flat)

# ── 배치 쿼리로 처리량 향상 ──
index = faiss.IndexFlatL2(dimension)
vectors = np.random.random((10000, dimension)).astype('float32')
index.add(vectors)

# 단일 쿼리 대신 배치 쿼리 (한 번에 여러 질의)
batch_queries = np.random.random((100, dimension)).astype('float32')
distances, indices = index.search(batch_queries, k=5)
print(f"배치 결과 shape: {indices.shape}")  # (100, 5)

# ── 멀티스레드 설정 ──
faiss.omp_set_num_threads(4)  # 사용할 CPU 코어 수 지정
```

### FAISS 장단점 정리

| 구분 | 내용 |
|------|------|
| 장점 | 초고속 검색, GPU 가속, 수십억 벡터 처리 가능, 다양한 인덱스 옵션 |
| 장점 | 메모리 내 동작으로 레이턴시 최소화, C++ 기반으로 매우 효율적 |
| 단점 | 메타데이터 관리 미지원 (별도 구현 필요) |
| 단점 | 영속성 미지원 (수동 직렬화 필요) |
| 단점 | 순수 라이브러리로 HTTP API 등 없음 — 애플리케이션 직접 통합 필요 |

> **핵심 포인트:** FAISS는 "빠른 벡터 탐색" 하나에 집중한 도구입니다. 완전한 벡터 DB 기능이 필요하다면 메타데이터 관리용 외부 저장소를 함께 구성해야 합니다. 수백만 개 이상의 벡터를 다루는 대규모 검색 시스템에서 최강의 선택입니다.

---

## 4. pgvector 실습

### pgvector 소개

pgvector는 PostgreSQL에 벡터 저장 및 유사도 검색 기능을 추가하는 오픈소스 확장(Extension)입니다. 기존 SQL 환경을 유지하면서 벡터 검색을 도입할 수 있다는 것이 가장 큰 강점입니다.

**실생활 비유:** pgvector는 기존에 사용하던 서류 캐비닛(PostgreSQL)에 특수 색인 탭(벡터 인덱스)을 추가하는 것과 같습니다. 캐비닛의 모든 기능(잠금장치, 분류 체계, 열람 권한)은 그대로 유지하면서, 내용 유사도 기반 검색이라는 새로운 능력만 추가됩니다.

**주요 특징:**
- PostgreSQL의 모든 기능(ACID 트랜잭션, 조인, 권한 관리) 그대로 사용 가능
- SQL WHERE 절과 벡터 검색을 자연스럽게 결합
- 기존 PostgreSQL 인프라(백업, 모니터링 등) 재사용 가능
- `<->` (L2 거리), `<#>` (내적), `<=>` (코사인 거리) 연산자 지원

### Docker로 pgvector 설치

```yaml
# docker-compose.yml -- PostgreSQL + pgvector
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: vectordb
    ports:
      - "5432:5432"
```

실행 명령어:
```bash
docker compose up -d
```

### pgvector 아키텍처

```mermaid
flowchart TB
    APP["애플리케이션\n(Python / psycopg2)"]
    PG["PostgreSQL 엔진"]
    EXT["pgvector 확장\n(vector 타입 + 연산자)"]
    IDX["HNSW / IVFFlat 인덱스\n(벡터 컬럼에 생성)"]
    TBL["테이블\ncontent TEXT, embedding vector(384)"]
    ACID["ACID 트랜잭션\n(자동 보장)"]
    SQL["SQL 필터\nWHERE category = 'programming'"]
    VSRCH["벡터 유사도 검색\nORDER BY embedding <=> query"]
    RESULT["결과 반환\n(SQL 결과셋 형태)"]

    APP --> PG
    PG --> EXT
    EXT --> IDX
    IDX --> TBL
    PG --> ACID
    APP --> SQL
    APP --> VSRCH
    SQL --> RESULT
    VSRCH --> RESULT

    style APP fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style PG fill:#0984e3,stroke:#74b9ff,color:#fff
    style EXT fill:#e17055,stroke:#fab1a0,color:#fff
    style IDX fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style TBL fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style ACID fill:#00b894,stroke:#55efc4,color:#fff
    style SQL fill:#fd79a8,stroke:#e84393,color:#fff
    style VSRCH fill:#fd79a8,stroke:#e84393,color:#fff
    style RESULT fill:#00b894,stroke:#55efc4,color:#fff
```

### pgvector SQL 연산자

| 연산자 | 의미 | 사용 예 |
|--------|------|---------|
| `<->` | L2(유클리드) 거리 | `ORDER BY embedding <-> query_vec` |
| `<#>` | 내적(음수) | `ORDER BY embedding <#> query_vec` |
| `<=>` | 코사인 거리 | `ORDER BY embedding <=> query_vec` |

### pgvector 인덱스 관리

pgvector는 두 가지 인덱스 타입을 지원하며, 데이터 규모와 정확도 요구사항에 따라 선택합니다.

| 인덱스 타입 | 알고리즘 | 특징 | 권장 시나리오 |
|-------------|----------|------|---------------|
| HNSW | 그래프 기반 근사 검색 | 빠른 검색, 높은 메모리 | 대부분의 프로덕션 환경 |
| IVFFlat | 클러스터 기반 근사 검색 | 낮은 메모리, 학습 필요 | 메모리 제한 환경 |

```sql
-- pgvector_index.sql -- pgvector 인덱스 생성 예시

-- HNSW 인덱스 (코사인 거리용)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat 인덱스 (L2 거리용, lists는 행 수의 제곱근 권장)
CREATE INDEX ON documents USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- 검색 시 정확도 파라미터 설정
SET hnsw.ef_search = 40;       -- HNSW: 탐색 깊이 (기본값 40)
SET ivfflat.probes = 10;       -- IVFFlat: 탐색 클러스터 수 (기본값 1)

-- 인덱스 적용 확인
EXPLAIN ANALYZE
SELECT content, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### pgvector 코드 예제

```python
# pgvector_example.py -- pgvector 사용법
import psycopg2
import numpy as np

conn = psycopg2.connect("postgresql://postgres:password@localhost/vectordb")
cursor = conn.cursor()

# ── 확장 활성화 ──
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

# ── 테이블 생성 ──
cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        category VARCHAR(50),
        embedding vector(384)
    )
""")

# ── 벡터 인덱스 생성 (HNSW) ──
cursor.execute("""
    CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING hnsw (embedding vector_cosine_ops)
""")

# ── 벡터 삽입 ──
embedding = np.random.random(384).tolist()
cursor.execute(
    "INSERT INTO documents (content, category, embedding) VALUES (%s, %s, %s)",
    ("Python 프로그래밍 가이드", "programming", str(embedding))
)

# ── 코사인 유사도 검색 ──
query_vector = np.random.random(384).tolist()
cursor.execute("""
    SELECT content, category, 1 - (embedding <=> %s) AS similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 5
""", (str(query_vector), str(query_vector)))

rows = cursor.fetchall()
for content, category, similarity in rows:
    print(f"[{category}] {content} (유사도: {similarity:.4f})")

# ── SQL 필터 + 벡터 검색 결합 ──
cursor.execute("""
    SELECT content, 1 - (embedding <=> %s) AS similarity
    FROM documents
    WHERE category = 'programming'
    ORDER BY embedding <=> %s
    LIMIT 5
""", (str(query_vector), str(query_vector)))

conn.commit()
conn.close()
```

> **핵심 포인트:** pgvector의 진정한 강점은 SQL 필터와 벡터 검색의 자연스러운 결합입니다. `WHERE category = 'programming' ORDER BY embedding <=> query` 한 줄로 "프로그래밍 카테고리 문서 중 가장 유사한 것"을 찾을 수 있습니다. 기존 PostgreSQL 인프라를 운용 중인 팀에게 가장 현실적인 선택입니다.

---

## 5. 실전 비교: 같은 작업을 세 가지 도구로

### 동일 작업 수행 비교

문서 5개를 저장하고 유사도 검색을 수행하는 동일한 작업을 세 도구로 수행할 때의 코드 복잡도를 비교합니다.

| 항목 | ChromaDB | FAISS | pgvector |
|------|----------|-------|----------|
| 초기 설정 코드 | 3줄 | 3줄 | 8줄 (DB 연결 + 확장) |
| 문서 추가 | 1회 함수 호출 | 벡터 변환 후 add | INSERT SQL 실행 |
| 메타데이터 저장 | 자동 통합 | 별도 dict 관리 | 일반 SQL 컬럼 |
| 유사도 검색 | query_texts() | index.search() | SELECT + ORDER BY |
| 필터링 | where={} 파라미터 | 별도 후처리 | WHERE 절 |
| 영속성 | PersistentClient | write_index() | 자동 (PostgreSQL) |
| 결과 형식 | dict (documents, distances) | numpy array | SQL 결과셋 |

### 특성 비교 다이어그램

```mermaid
flowchart LR
    CENTER["벡터 DB 선택 기준"]

    CENTER --> CHROMA_NODE["ChromaDB"]
    CENTER --> FAISS_NODE["FAISS"]
    CENTER --> PGV_NODE["pgvector"]

    CHROMA_NODE --> C1["편의성 최상, 자동 임베딩"]
    CHROMA_NODE --> C2["메타데이터 내장, 확장성 중간"]

    FAISS_NODE --> F1["검색 속도 최상, GPU 지원"]
    FAISS_NODE --> F2["메타데이터 별도, 임베딩 별도"]

    PGV_NODE --> P1["SQL 통합 최상, ACID 지원"]
    PGV_NODE --> P2["확장성 높음, 편의성 중간"]

    style CENTER fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style CHROMA_NODE fill:#0984e3,stroke:#74b9ff,color:#fff
    style FAISS_NODE fill:#e17055,stroke:#fab1a0,color:#fff
    style PGV_NODE fill:#00b894,stroke:#55efc4,color:#fff
    style C1 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style C2 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style F1 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style F2 fill:#fab1a0,stroke:#e17055,color:#2d3436
    style P1 fill:#55efc4,stroke:#00b894,color:#2d3436
    style P2 fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 종합 비교 테이블

| 비교 항목 | ChromaDB | FAISS | pgvector |
|-----------|----------|-------|----------|
| 유형 | 전용 벡터 DB | 벡터 검색 라이브러리 | PostgreSQL 확장 |
| 설치 | pip install | pip install | Docker + 확장 설치 |
| 자동 임베딩 | 지원 | 미지원 | 미지원 |
| 메타데이터 | 내장 지원 | 별도 구현 필요 | SQL 컬럼으로 관리 |
| 필터링 | where={} | 후처리 필요 | SQL WHERE |
| 영속성 | 선택 가능 | 수동 저장/로드 | 자동 (PostgreSQL) |
| 트랜잭션 | 미지원 | 미지원 | ACID 완전 지원 |
| 최대 벡터 수 | ~수백만 | 수십억+ | ~수천만 |
| GPU 가속 | 미지원 | 지원 | 미지원 |
| 운영 복잡도 | 낮음 | 낮음~중간 | 중간~높음 |
| 비용 | 오픈소스 (무료) | 오픈소스 (무료) | 오픈소스 (무료) |
| 최적 시나리오 | LLM 앱, RAG 프로토타입 | 대규모 ANN 검색 | 기존 SQL 인프라 통합 |

> **핵심 포인트:** ChromaDB는 속도보다 개발 편의성을, FAISS는 편의성보다 속도와 규모를, pgvector는 새로운 인프라 도입 없이 기존 SQL 환경 내 벡터 검색을 원하는 팀에게 최적입니다.

---

## 6. RAG 실전 파이프라인 미니 프로젝트

### 미니 RAG 파이프라인 개요

ChromaDB를 활용한 간단한 RAG(Retrieval-Augmented Generation) 파이프라인을 구축합니다. 문서를 로드하고 청킹한 뒤 임베딩하여 저장하고, 질문이 들어오면 관련 문서를 검색하여 LLM에 컨텍스트로 제공합니다.

**실생활 비유:** RAG 파이프라인은 시험 공부를 도와주는 조교와 같습니다. 조교는 먼저 교재(문서)를 작은 단락으로 나눠(청킹) 색인을 만들어 놓습니다(임베딩 + 저장). 학생이 질문하면 색인에서 관련 단락을 찾아(검색) 교수(LLM)에게 "이 내용을 참고해서 답변해 주세요"라고 전달합니다.

### 미니 RAG 파이프라인 플로우

```mermaid
flowchart TB
    DOCS["원본 문서\n(텍스트 파일, PDF 등)"]
    CHUNK["청킹\n(문서를 작은 단락으로 분리)"]
    EMBED["임베딩\n(각 단락을 벡터로 변환)"]
    STORE["ChromaDB 저장\n(벡터 + 메타데이터)"]
    QUESTION["사용자 질문"]
    Q_EMBED["질문 임베딩\n(쿼리 벡터 생성)"]
    RETRIEVE["유사 문서 검색\n(Top-K 검색)"]
    CONTEXT["컨텍스트 구성\n(검색된 단락 조합)"]
    LLM["LLM 호출\n(OpenAI GPT 등)"]
    ANSWER["최종 답변 생성"]

    DOCS --> CHUNK
    CHUNK --> EMBED
    EMBED --> STORE
    QUESTION --> Q_EMBED
    Q_EMBED --> RETRIEVE
    STORE --> RETRIEVE
    RETRIEVE --> CONTEXT
    CONTEXT --> LLM
    LLM --> ANSWER

    style DOCS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style CHUNK fill:#0984e3,stroke:#74b9ff,color:#fff
    style EMBED fill:#0984e3,stroke:#74b9ff,color:#fff
    style STORE fill:#00b894,stroke:#55efc4,color:#fff
    style QUESTION fill:#e17055,stroke:#fab1a0,color:#fff
    style Q_EMBED fill:#e17055,stroke:#fab1a0,color:#fff
    style RETRIEVE fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style CONTEXT fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style LLM fill:#fd79a8,stroke:#e84393,color:#fff
    style ANSWER fill:#00b894,stroke:#55efc4,color:#fff
```

### 미니 RAG 파이프라인 코드

```python
# rag_mini_pipeline.py -- ChromaDB + OpenAI를 활용한 미니 RAG 파이프라인
import chromadb
from openai import OpenAI

# ── 설정 ──
openai_client = OpenAI(api_key="YOUR_API_KEY")
chroma_client = chromadb.PersistentClient(path="./rag_db")

# ── 임베딩 함수 ──
def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# ── 컬렉션 준비 ──
collection = chroma_client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"}
)

# ── 문서 인덱싱 ──
def index_documents(documents: list[dict]):
    """문서 리스트를 받아 ChromaDB에 저장합니다."""
    for i, doc in enumerate(documents):
        embedding = get_embedding(doc["content"])
        collection.add(
            embeddings=[embedding],
            documents=[doc["content"]],
            metadatas=[{"source": doc.get("source", "unknown")}],
            ids=[f"doc_{i}"]
        )
    print(f"{len(documents)}개 문서 인덱싱 완료")

# ── RAG 검색 및 답변 생성 ──
def rag_query(question: str, top_k: int = 3) -> str:
    # 1. 질문 임베딩
    query_embedding = get_embedding(question)

    # 2. 유사 문서 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 3. 컨텍스트 구성
    context_docs = results["documents"][0]
    context = "\n\n".join([f"[문서 {i+1}]\n{doc}"
                           for i, doc in enumerate(context_docs)])

    # 4. LLM 호출
    prompt = f"""다음 문서들을 참고하여 질문에 답변해 주십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ── 실행 예시 ──
sample_docs = [
    {"content": "Python은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.", "source": "wiki"},
    {"content": "RAG는 검색 증강 생성으로, 외부 지식을 활용하여 LLM의 답변 품질을 높입니다.", "source": "ai_blog"},
    {"content": "벡터 데이터베이스는 고차원 벡터를 저장하고 유사도 기반으로 검색합니다.", "source": "db_docs"},
]
index_documents(sample_docs)
answer = rag_query("Python은 누가 만들었나요?")
print(answer)
```

> **핵심 포인트:** 미니 RAG 파이프라인의 핵심은 "검색이 LLM보다 먼저"라는 점입니다. 질문에 맞는 관련 문서를 먼저 찾아 컨텍스트로 제공함으로써, LLM이 학습 데이터에 없는 최신 정보나 도메인 지식도 정확하게 답변할 수 있습니다.

---

## 7. 벡터 DB 선택 가이드

### 시나리오별 추천

실제 프로젝트에서 벡터 DB를 선택할 때 고려해야 할 요소와 각 상황에 맞는 추천 도구를 정리합니다.

| 시나리오 | 추천 도구 | 이유 |
|----------|-----------|------|
| 빠른 프로토타입 / 학습 | ChromaDB | 설치 쉬움, 자동 임베딩, 코드 단순 |
| 수백만~수십억 벡터 검색 | FAISS | 최고 성능, GPU 가속, 메모리 효율 |
| 기존 PostgreSQL 인프라 보유 | pgvector | SQL 통합, 트랜잭션, 추가 인프라 없음 |
| 클라우드 매니지드 서비스 필요 | Pinecone | 서버리스, 완전 관리형, 자동 확장 |
| 멀티모달 + 그래프 검색 | Weaviate | 텍스트/이미지/비디오 통합 검색 |
| 엔터프라이즈 + 하이브리드 검색 | Elasticsearch + dense_vector | 키워드 + 벡터 하이브리드 검색 |

### 선택 의사결정 플로우차트

```mermaid
flowchart LR
    START["선택 시작"] --> Q1{"PostgreSQL 인프라?"}
    Q1 -- "예" --> PGV["pgvector"]
    Q1 -- "아니오" --> Q2{"1억 개 이상?"}
    Q2 -- "예" --> MIXED["FAISS + 메타 DB"]
    Q2 -- "아니오" --> Q3{"매니지드 필요?"}
    Q3 -- "예" --> PINE["Pinecone"]
    Q3 -- "아니오" --> Q4{"프로토타입/학습?"}
    Q4 -- "예" --> CHROMA["ChromaDB"]
    Q4 -- "아니오" --> Q5{"멀티모달?"}
    Q5 -- "예" --> WEAV["Weaviate"]
    Q5 -- "아니오" --> FAISS["FAISS"]

    style START fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style Q1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style Q2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style Q3 fill:#0984e3,stroke:#74b9ff,color:#fff
    style Q4 fill:#0984e3,stroke:#74b9ff,color:#fff
    style Q5 fill:#0984e3,stroke:#74b9ff,color:#fff
    style PGV fill:#00b894,stroke:#55efc4,color:#fff
    style FAISS fill:#e17055,stroke:#fab1a0,color:#fff
    style PINE fill:#fd79a8,stroke:#e84393,color:#fff
    style CHROMA fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style WEAV fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style MIXED fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 비용 및 운영 관점

| 항목 | ChromaDB | FAISS | pgvector | Pinecone |
|------|----------|-------|----------|----------|
| 라이선스 | 오픈소스 (Apache 2.0) | 오픈소스 (MIT) | 오픈소스 (PostgreSQL) | 상용 (무료 티어 있음) |
| 인프라 비용 | 서버 비용만 | 서버 비용만 | 서버 비용만 | 사용량 기반 과금 |
| 운영 부담 | 낮음 | 낮음~중간 | 중간 (PostgreSQL 운영) | 없음 (완전 관리형) |
| 스케일아웃 | 수동 구성 | 수동 구성 | PostgreSQL 복제 활용 | 자동 |

> **핵심 포인트:** 벡터 DB 선택은 기술적 성능만의 문제가 아닙니다. 팀의 인프라 역량, 운영 부담, 예산, 데이터 규모를 종합적으로 고려해야 합니다. "가장 좋은" 벡터 DB는 존재하지 않으며, 상황에 가장 잘 맞는 도구를 선택하는 것이 올바른 접근 방식입니다.

---

## 8. 핵심 정리

### 3개 구현체 최종 비교 요약

| 항목 | ChromaDB | FAISS | pgvector |
|------|----------|-------|----------|
| 유형 | 전용 벡터 DB | 벡터 검색 라이브러리 | PostgreSQL 확장 |
| 사용 편의성 | 최상 | 중간 | 중간 |
| 검색 성능 | 중간 | 최상 | 중간~높음 |
| 자동 임베딩 | 지원 | 미지원 | 미지원 |
| 메타데이터 관리 | 내장 | 별도 구현 | SQL 컬럼 |
| 영속성 | 선택 가능 | 수동 | 자동 |
| 트랜잭션 | 미지원 | 미지원 | 완전 지원 |
| 최대 규모 | 수백만 | 수십억+ | 수천만 |
| GPU 가속 | 미지원 | 지원 | 미지원 |
| 추천 시나리오 | RAG 프로토타입, LLM 앱 | 대규모 ANN 검색 | SQL 통합 환경 |

### 핵심 요약

**ChromaDB**는 LLM 애플리케이션과 RAG 파이프라인을 빠르게 개발할 때 최적입니다. 자동 임베딩과 메타데이터 필터링이 내장되어 있어 코드 복잡도가 낮고, 인메모리와 영속 저장을 유연하게 전환할 수 있습니다.

**FAISS**는 순수 벡터 탐색 성능이 가장 뛰어납니다. 메타데이터 관리나 영속성은 직접 구현해야 하지만, 수십억 개의 벡터를 밀리초 단위로 검색해야 하는 대규모 시스템에서는 대체 불가능한 선택입니다.

**pgvector**는 기존 PostgreSQL 인프라를 보유한 팀에게 가장 현실적인 선택입니다. SQL 필터와 벡터 검색을 자연스럽게 결합할 수 있고, ACID 트랜잭션과 기존 운영 도구를 그대로 활용할 수 있습니다.

| 학습 단계 | 권장 경로 |
|-----------|-----------|
| 입문 | ChromaDB로 벡터 DB 개념 습득 |
| 중급 | FAISS로 인덱스 타입과 ANN 알고리즘 이해 |
| 실전 | pgvector로 프로덕션 환경 SQL 통합 구성 |

### 다음 강의 미리보기

다음 강의인 **바이너리 저장과 성능 최적화**(`13_binary_storage_and_performance.md`)에서는 대용량 데이터를 효율적으로 저장하는 바이너리 포맷(Parquet, HDF5, NumPy `.npy`)과 데이터베이스 성능 최적화 기법(인덱스 튜닝, 쿼리 최적화, 파티셔닝)을 학습합니다. 벡터 DB에 저장되는 임베딩 데이터를 효율적으로 관리하는 방법까지 연결하여 학습합니다.

---

> **이전 강의:** [벡터 데이터베이스의 이해](11_vector_databases.md)
>
> **다음 강의:** [바이너리 저장과 성능 최적화](13_binary_storage_and_performance.md)
