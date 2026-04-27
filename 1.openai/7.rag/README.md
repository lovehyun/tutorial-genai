# RAG (Retrieval-Augmented Generation)

벡터 검색 기반 RAG 파이프라인을 FAISS와 ChromaDB 두 가지 벡터 저장소로 구현합니다.

## RAG 파이프라인

```
문서 → 임베딩(벡터 변환) → 벡터 DB 저장 → 질문 임베딩 → 유사도 검색 → LLM 응답 생성
```

## 예제 구조

```
7.rag/
├── 1.faiss/           ← FAISS 기반 벡터 검색
│   ├── 1.faiss.py                      기본 RAG
│   ├── 2.faiss_info.py                 상세 정보 (유사도, 토큰)
│   ├── 3.faiss_localembed.py           로컬 임베딩 (MiniLM, L2)
│   ├── 3.faiss_localembed2_cosine.py   로컬 임베딩 (MiniLM, 코사인)
│   ├── 3.faiss_localembed3_model.py    로컬 임베딩 (MPNet, L2)
│   ├── 3.faiss_localembed4_model_cosine.py  로컬 임베딩 (MPNet, 코사인)
│   ├── 4.faiss_localmodel.py           완전 로컬 (API 불필요)
│   └── 5.faiss_gpu.py                  GPU 가속
└── vectordb.md       ← 벡터 DB 개념 정리
```

## 1.faiss/ — FAISS 예제 상세

| 파일 | 임베딩 | 유사도 | LLM | 구현 범위 |
|------|--------|--------|-----|----------|
| `1.faiss.py` | OpenAI API | L2 거리 | GPT-4o-mini | 기본 RAG: 3개 문서 임베딩 → top-1 검색 → GPT 응답 |
| `2.faiss_info.py` | OpenAI API | L2 → 유사도 변환 | GPT-4o-mini | 1번 확장: 유사도 점수 출력, tiktoken 토큰 수 계산, 저품질 경고 |
| `3.faiss_localembed.py` | 로컬 (MiniLM) | L2 거리 | GPT-4 | 임베딩만 로컬로 교체 (API 비용 절감), 응답은 여전히 OpenAI |
| `3.faiss_localembed2_cosine.py` | 로컬 (MiniLM) | 코사인 (IndexFlatIP) | GPT-4 | L2 대신 코사인 유사도 사용, 벡터 정규화 + Inner Product |
| `3.faiss_localembed3_model.py` | 로컬 (MPNet) | L2 거리 | GPT-4 | 더 좋은 임베딩 모델(all-mpnet-base-v2)로 교체 |
| `3.faiss_localembed4_model_cosine.py` | 로컬 (MPNet) | 코사인 (IndexFlatIP) | GPT-4 | 최고 모델 + 코사인 유사도 조합 (최적 구성) |
| `4.faiss_localmodel.py` | 로컬 (MiniLM) | L2 거리 | 없음 | 완전 로컬: 검색만 수행, LLM 응답 없음 (API 불필요) |
| `5.faiss_gpu.py` | 없음 | L2 거리 | 없음 | GPU 가속 데모: 1000개 랜덤 벡터에서 top-5 검색 (Linux 전용) |

**학습 순서**: 1 → 2 → 3 → 3_cosine → 3_model → 3_model_cosine → 4 → 5

```
1.기본 RAG → 2.상세 정보 → 3.로컬 임베딩(4가지 변형) → 4.완전 로컬 → 5.GPU
  (OpenAI)    (유사도/토큰)   (MiniLM/MPNet × L2/코사인)   (API 없음)    (가속)
```

## 설치

```bash
# FAISS
pip install openai faiss-cpu sentence-transformers
# GPU 버전: pip install faiss-gpu

# ChromaDB
pip install openai chromadb sentence-transformers tiktoken
```

---

## 벡터 데이터베이스 비교

### 주요 벡터 DB 비교표

| VectorDB | 유형 | 설치 난이도 | 한줄 설명 | 최대 벡터 수 | 라이선스 |
|----------|------|-----------|----------|------------|---------|
| **FAISS** | 라이브러리 | 쉬움 (pip) | Meta의 고속 벡터 검색 라이브러리 | 수십억+ | MIT |
| **ChromaDB** | 임베디드 DB | 쉬움 (pip) | AI 네이티브 오픈소스 벡터 DB | 수백만 | Apache 2.0 |
| **pgvector** | PostgreSQL 확장 | 중간 | PostgreSQL에 벡터 검색 추가 | 수천만 | PostgreSQL |
| **Pinecone** | 관리형 SaaS | 쉬움 (API) | 서버리스 벡터 DB (클라우드) | 수십억+ | 상용 |
| **Weaviate** | 서버형 DB | 중간 (Docker) | GraphQL 기반 벡터 DB | 수십억 | BSD-3 |
| **Qdrant** | 서버형 DB | 중간 (Docker) | Rust 기반 고성능 벡터 DB | 수십억 | Apache 2.0 |
| **Milvus** | 분산 DB | 어려움 (K8s) | 대규모 분산 벡터 DB | 수백억+ | Apache 2.0 |
| **LanceDB** | 임베디드 DB | 쉬움 (pip) | 서버리스 벡터 DB (로컬 파일) | 수백만 | Apache 2.0 |

### 상세 비교

| 기능 | FAISS | ChromaDB | pgvector | Pinecone | Qdrant | Milvus |
|------|-------|----------|----------|----------|--------|--------|
| **메타데이터 저장** | X | O | O | O | O | O |
| **메타데이터 필터링** | X | O | O (SQL) | O | O | O |
| **영속 저장** | 수동 | 자동 | 자동 | 클라우드 | 자동 | 자동 |
| **분산 처리** | X | X | X | O | O | O |
| **GPU 가속** | O | X | X | 내부 | X | O |
| **실시간 CRUD** | 어려움 | O | O | O | O | O |
| **내장 임베딩** | X | O | X | X | X | X |
| **Python API** | O | O | O (psycopg2) | O | O | O |
| **서버 불필요** | O | O | X (PG 필요) | X (클라우드) | X (Docker) | X (Docker/K8s) |

### 용도별 추천

| 사용 사례 | 추천 | 이유 |
|----------|------|------|
| **학습/프로토타이핑** | ChromaDB | pip install만으로 즉시 사용, 내장 임베딩 |
| **고속 대량 검색** | FAISS | 수십억 벡터도 밀리초 검색, GPU 지원 |
| **이미 PostgreSQL 사용** | pgvector | 기존 DB에 벡터 검색만 추가 |
| **서버 관리 싫음** | Pinecone / LanceDB | Pinecone: 완전 관리형 / LanceDB: 로컬 파일 |
| **프로덕션 자체 운영** | Qdrant / Milvus | Qdrant: 단일 서버 / Milvus: 대규모 분산 |
| **LangChain 연동** | ChromaDB / FAISS | LangChain에서 가장 잘 지원 |

### 아키텍처 비교

```
[ 라이브러리 ]          [ 임베디드 DB ]         [ 서버형 DB ]          [ 관리형 SaaS ]
   FAISS                ChromaDB               Qdrant                Pinecone
                        LanceDB                Weaviate
                                               Milvus

← 단순/가벼움                                                   복잡/확장성 →
← 로컬 전용                                                     클라우드/분산 →
← 벡터 검색만                                           메타데이터/필터/CRUD →
```

### pgvector 참고

PostgreSQL을 이미 사용하는 환경이라면 pgvector가 가장 자연스러운 선택입니다:

```sql
-- PostgreSQL에서 벡터 검색 활성화
CREATE EXTENSION vector;

-- 벡터 컬럼이 있는 테이블 생성
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI 임베딩 차원
);

-- 유사도 검색 (코사인 거리)
SELECT content, 1 - (embedding <=> query_vector) AS similarity
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 5;
```

---

## FAISS vs ChromaDB 핵심 차이

| 항목 | FAISS (1.faiss/) | ChromaDB (2.chromadb/) |
|------|-----------------|----------------------|
| 성격 | 벡터 검색 **라이브러리** | 벡터 **데이터베이스** |
| 임베딩 관리 | numpy 배열 직접 관리 | 내장 임베딩 함수로 자동 |
| 메타데이터 | 별도 관리 필요 | 자동 저장 + 필터링 |
| 영속 저장 | `faiss.write_index()` 수동 | `PersistentClient` 자동 |
| 문서 삭제 | 인덱스 재구축 필요 | `collection.delete()` |
| 적합한 상황 | 대규모 고속 검색, GPU 활용 | 프로토타이핑, 소중규모 앱 |
| 코드량 | 많음 (boilerplate) | 적음 (추상화 높음) |

---

## 유사도 측정 방식: L2 vs 코사인

### L2 (유클리드 거리) — "두 점 사이의 직선 거리"

```
A(1,3) ●
        \  거리 = √((4-1)² + (1-3)²) = 3.6
         \
          ● B(4,1)
```

- 값: 0(동일) ~ 무한대(멀수록 큼)
- 벡터 **크기(길이)에 영향**을 받음
- FAISS: `IndexFlatL2`

### 코사인 유사도 — "두 화살표의 방향이 얼마나 같은지"

```
        A ↗  (방향 비슷 → 유사도 높음)
        B ↗
        C ←  (방향 반대 → 유사도 낮음)
```

- 값: -1(정반대) ~ 0(무관) ~ 1(동일 방향)
- 벡터 **크기 무시, 방향만** 비교
- **텍스트 검색에 더 적합** (문서 길이가 달라도 의미만 비교)
- FAISS: `IndexFlatIP` + 벡터 정규화

### 예제에서의 사용

| 파일 | 방식 | FAISS 인덱스 | 정규화 |
|------|------|-------------|--------|
| `1.faiss.py` | L2 | IndexFlatL2 | 불필요 |
| `3.faiss_localembed2_cosine.py` | 코사인 | IndexFlatIP | 필요 (normalize_vector) |
| `1.chromadb.py` | L2 (기본) | - | - |
| `2.chromadb_info.py` | 코사인 | `hnsw:space=cosine` | ChromaDB가 자동 처리 |

---

## 임베딩 모델 비교

### 임베딩이란?

```
"인공지능은 미래 기술이다" → [0.023, -0.15, 0.87, ...] (384~3072차원 벡터)
"AI is future technology"  → [0.021, -0.14, 0.85, ...] (비슷한 의미 → 비슷한 벡터)
"오늘 점심 뭐 먹지?"       → [-0.45, 0.32, 0.01, ...] (다른 의미 → 다른 벡터)
```

텍스트의 **의미**를 숫자 벡터로 변환하는 모델입니다. RAG에서 "검색"을 담당합니다.

### 주요 임베딩 모델 비교표

| 모델 | 개발사 | 차원 | 크기 | 위치 | 한국어 | 품질 | 비용 |
|------|--------|------|------|------|--------|------|------|
| **text-embedding-3-large** | OpenAI | 3072 | - | API | O | ★★★★★ | $0.13/1M 토큰 |
| **text-embedding-3-small** | OpenAI | 1536 | - | API | O | ★★★★☆ | $0.02/1M 토큰 |
| **text-embedding-ada-002** | OpenAI | 1536 | - | API | O | ★★★★☆ | $0.10/1M 토큰 |
| **all-mpnet-base-v2** | HuggingFace | 768 | 420MB | 로컬 | △ | ★★★★☆ | 무료 |
| **all-MiniLM-L6-v2** | HuggingFace | 384 | 80MB | 로컬 | △ | ★★★☆☆ | 무료 |
| **bge-m3** | BAAI (Beijing) | 1024 | 2.2GB | 로컬 | O | ★★★★★ | 무료 |
| **multilingual-e5-large** | Microsoft | 1024 | 2.2GB | 로컬 | O | ★★★★☆ | 무료 |
| **paraphrase-multilingual-MiniLM-L12-v2** | HuggingFace | 384 | 470MB | 로컬 | O | ★★★☆☆ | 무료 |
| **KoSimCSE-roberta** | KakaoBrain | 768 | 1.1GB | 로컬 | ★★★★★ | ★★★★☆ | 무료 |
| **Cohere embed-v3** | Cohere | 1024 | - | API | O | ★★★★★ | 유료 |
| **Voyage AI voyage-3** | Voyage AI | 1024 | - | API | O | ★★★★★ | 유료 |

### 임베딩 모델 유형

| 유형 | 대표 모델 | 특징 | 적합한 상황 |
|------|----------|------|------------|
| **API 기반** | OpenAI, Cohere, Voyage | 설치 불필요, 고품질 | 인터넷 연결 가능, 비용 허용 |
| **범용 영어** | MiniLM, MPNet | 가볍고 빠름 | 영어 위주 프로토타이핑 |
| **다국어** | bge-m3, multilingual-e5 | 100+ 언어 지원 | **한국어 RAG에 추천** |
| **한국어 특화** | KoSimCSE | 한국어 최적화 | 한국어 전용 서비스 |
| **코드 특화** | voyage-code-3, codebert | 소스코드 임베딩 | 코드 검색/RAG |

### 예제에서 사용하는 모델 상세

**all-MiniLM-L6-v2** (예제: 3.faiss_localembed.py, 5.chromadb_localmodel.py)
- BERT 6레이어 경량 모델, 80MB
- 속도 빠름, 영어에 최적화
- 한국어는 의미가 뭉개질 수 있음 (학습용으로는 충분)

**all-mpnet-base-v2** (예제: 3.faiss_localembed3_model.py)
- MPNet 12레이어 모델, 420MB
- MiniLM보다 정확하지만 2배 느림
- 영어 sentence-transformers 중 최고 성능

---

## 임베딩 모델 호환성과 교체 규칙

### 핵심 규칙: 임베딩 모델을 바꾸면 벡터 DB를 재구축해야 한다

```
[저장 시] 문서 → MiniLM(384차원) → 벡터 DB에 저장
[검색 시] 질문 → MPNet(768차원) → 벡터 DB에서 검색  ← 차원 불일치! 오류 발생!
```

| 상황 | 결과 |
|------|------|
| 저장과 검색에 **같은** 임베딩 모델 | 정상 동작 |
| 저장과 검색에 **다른** 임베딩 모델 | 차원 불일치 → 오류 또는 엉터리 결과 |
| 임베딩 모델 업그레이드 | **전체 문서 재임베딩 필요** |

### 임베딩 모델 vs LLM — 역할이 다르다

```
                    임베딩 모델                        LLM
                    (검색 담당)                     (응답 생성 담당)
                        │                              │
문서 → [MiniLM] → 벡터 DB    질문 → 벡터 DB → 검색 결과 → [GPT-4o-mini] → 답변
                                                        ↑
                                          여기는 자유롭게 교체 가능!
```

| 구성 요소 | 역할 | 교체 시 영향 | 예시 |
|----------|------|------------|------|
| **임베딩 모델** | 텍스트 → 벡터 변환 | DB 재구축 필요 | MiniLM, MPNet, OpenAI |
| **벡터 DB** | 벡터 저장 + 검색 | 데이터 마이그레이션 필요 | FAISS, ChromaDB |
| **LLM (추론)** | 검색 결과 → 답변 생성 | **자유롭게 교체 가능** | GPT-4o-mini, GPT-4, Ollama |

### 자유롭게 조합할 수 있는 것

```
임베딩: OpenAI ada-002   +  벡터DB: FAISS     +  LLM: GPT-4        ← OK
임베딩: MiniLM (로컬)    +  벡터DB: ChromaDB  +  LLM: Ollama       ← OK (완전 무료)
임베딩: bge-m3 (로컬)    +  벡터DB: FAISS     +  LLM: GPT-4o-mini     ← OK
임베딩: OpenAI ada-002   +  벡터DB: ChromaDB  +  LLM: Claude       ← OK
```

**규칙**: 임베딩 모델은 저장/검색에서 **반드시 동일**해야 하고, LLM은 **아무거나** 써도 됩니다.

### 임베딩 모델 교체 시 체크리스트

1. 새 모델의 **벡터 차원** 확인 (384? 768? 1024? 1536?)
2. FAISS: `IndexFlatL2(새_차원)` 으로 인덱스 재생성
3. ChromaDB: 기존 컬렉션 삭제 → 새 임베딩 함수로 재생성
4. **모든 문서를 새 모델로 재임베딩**
5. 검색 시에도 반드시 같은 모델로 질문 임베딩

### 한국어 RAG 추천 구성

| 환경 | 임베딩 | 벡터 DB | LLM | 비용 |
|------|--------|---------|-----|------|
| **완전 무료** | bge-m3 (로컬) | ChromaDB | Ollama (EXAONE 3.5) | 0원 |
| **저비용** | bge-m3 (로컬) | ChromaDB | GPT-4o-mini-turbo | 최소 |
| **고품질** | OpenAI text-embedding-3-large | ChromaDB | GPT-4 | 중간 |
| **프로덕션** | OpenAI text-embedding-3-large | Qdrant | GPT-4 | 높음 |

### GPU 가속 vs CPU

| | CPU 모드 | GPU 모드 |
|--|----------|---------|
| **패키지** | `faiss-cpu` (pip) | `faiss-gpu` (Linux 전용) |
| **속도** | 수천 벡터: 밀리초 / 수백만: 수초 | 수백만 벡터도 밀리초 |
| **메모리** | RAM 사용 | VRAM 사용 |
| **필요한 경우** | 예제/학습/소규모 | 수백만 벡터 이상 프로덕션 |
| **예제** | 1~4번 전체 | `5.faiss_gpu.py`만 |

이 예제의 1~4번은 전부 CPU로 동작하며, 문서 수백~수천 개 수준에서는 GPU 없이도 충분합니다.
