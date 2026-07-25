# RAG (Retrieval-Augmented Generation)

FAISS 벡터 검색을 직접 다루며 RAG 파이프라인의 **내부 동작 원리**를 배웁니다.
한 단계에 개념 하나씩 더해가는 구조입니다.

## RAG 파이프라인

```
문서 → 임베딩(벡터화) → FAISS 저장 → 질문 임베딩 → 유사도 검색 → GPT 응답 생성
```

LLM에게 질문만 주지 않고 **관련 문서를 먼저 찾아 함께** 줘서, 모델이 모르는
최신·사내 정보도 답할 수 있게 하는 방식입니다.

## 학습 순서

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.rag_basic.py` | 기본 RAG 파이프라인 (OpenAI 임베딩 + FAISS L2 + GPT) |
| `2.rag_similarity_score.py` | 검색 품질 점검 — 유사도 점수, 저품질 경고, 토큰 수 |
| `3.rag_local_embedding.py` | 임베딩을 로컬 모델(MiniLM)로 교체 — 비용 0원 |
| `4.rag_cosine_similarity.py` | 거리척도를 L2 → 코사인 유사도로 변경 |
| `5.rag_better_embedding_model.py` | 더 정확한 임베딩 모델(MPNet)로 교체·비교 |

부록: `faiss_gpu.py` — GPU 가속 (선택, Linux 전용, 빌드업 외)

## 설치

```bash
pip install openai faiss-cpu numpy sentence-transformers tiktoken python-dotenv
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`

## 왜 FAISS인가 — FAISS vs ChromaDB

이 폴더는 **순수 FAISS**를 씁니다. FAISS는 벡터 검색 *라이브러리*라서
임베딩·거리척도·정규화를 직접 다뤄야 하고, 그래서 "벡터 검색이 내부에서
무슨 일을 하는지"를 배우기에 좋습니다.

| 항목 | FAISS | ChromaDB |
|------|-------|----------|
| 성격 | 벡터 검색 **라이브러리** (저수준) | 벡터 **데이터베이스** (고수준) |
| 저장 대상 | 벡터만 (문서·메타데이터는 직접 관리) | 벡터 + 원문 + 메타데이터 |
| 영속 저장 | 수동 (`faiss.write_index`) | 자동 (`PersistentClient`) |
| 메타데이터 필터 | 없음 | `where` 절 지원 |
| 학습 측면 | 원리가 다 드러남 | 원리는 감춰지고 앱 개발이 쉬움 |

> ChromaDB(고수준, 프레임워크 연동)는 `2.langchain/7.RAG`에서 다룹니다.
> 더 많은 벡터 DB 비교는 [vectordb.md](vectordb.md) 참고.

## 핵심 개념: L2 vs 코사인 유사도 (4단계)

| | L2 (유클리드 거리) | 코사인 유사도 |
|--|-------------------|--------------|
| 비교 대상 | 두 점 사이의 직선 거리 | 두 벡터의 방향 |
| 벡터 크기 영향 | 받음 | 무시 (방향만 비교) |
| 값 | 0(동일) ~ ∞ | -1(반대) ~ 1(동일) |
| FAISS 인덱스 | `IndexFlatL2` | `IndexFlatIP` + 벡터 정규화 |
| 텍스트 검색 적합도 | 보통 | **우수** (문서 길이 무관, 의미만 비교) |

## 핵심 규칙: 임베딩 모델 일치 (3·5단계)

- 문서 저장과 질문 검색은 **반드시 같은 임베딩 모델**을 써야 합니다.
- 모델을 바꾸면 벡터 차원이 달라지므로(MiniLM 384 ↔ MPNet 768) **인덱스를 재구축**해야 합니다.
- 반면 응답 생성용 LLM(GPT 등)은 검색과 무관하므로 자유롭게 교체할 수 있습니다.
