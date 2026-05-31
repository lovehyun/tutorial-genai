# RAG (Retrieval-Augmented Generation)

LLM 응답에 **외부 문서 검색 결과를 반영**하여 정확도와 신뢰도를 높이는 패턴.

각 폴더는 **한 가지 개념** 에 집중하며, 같은 폴더 안에서는 **핵심 → 빌드업** 순서.

## 폴더 구조

```
7.RAG/
├── DATA/                       ← 공통 데이터 (nvme.txt / ssd.txt / 시큐어코딩 PDF / 학술대회 CFP PDF)
├── README.md                   ← 이 파일
│
├── 1.basics/                   ← RAG 의 출발 — 임베딩이 뭔지부터
├── 2.loaders/                  ← 텍스트 / PDF 로더 + 청크 전략
├── 3.vectorstore/              ← ChromaDB 영속화 + 검색 유틸
├── 4.rag_chain/                ← 표준 LCEL RAG 체인 + 출처 인용
├── 5.conversational/           ← 대화형 RAG (history-aware)
├── 6.agentic/                  ← Agentic RAG (기본 → 루프 → LangGraph 고도화)
├── 7.local_model/              ← 로컬 LLM 으로 RAG
│   ├── 1.ollama/               ← Ollama 기반
│   └── 2.huggingface/          ← HuggingFace 기반 (인기 모델 + 한국어 특화)
└── 8.web_app/                  ← Flask 풀스택 (점진 빌드업)
    ├── 1.minimal/
    ├── 2.with_score/
    ├── 3.file_manage/           ← 템플릿(HTML) 버전 — 업로드/질문/삭제 풀스택
    └── 4.file_manager_restapi/  ← 같은 기능을 템플릿 없이 순수 REST API 로
```

> **방침**
> - 모든 예제는 라이브 코딩 가능한 길이 (~30~120줄)
> - 각 파일 상단에 (1) 모듈 한 줄 정의 + (2) 이 예제의 목적 명시
> - 같은 폴더 안에서는 변수/함수 이름 일관 → diff 로 빌드업 차이 한눈에 보임
> - 데이터는 모두 `../DATA/` 경유 (서브 폴더에선 `../../DATA/`)

## 학습 흐름

```
1.basics       ─ 임베딩 / 유사도 / in-memory 검색 / 첫 RAG 체인
       ↓
2.loaders      ─ 텍스트·PDF 로딩 + 청크 전략 + 메타데이터
       ↓
3.vectorstore  ─ ChromaDB 영속화 / 검색 모드 / 다중 컬렉션
       ↓
4.rag_chain    ─ 표준 LCEL RAG / 출처 인용 / 빌트인 체인
       ↓
5.conversational ─ 후속 질문 처리 / history-aware retriever
       ↓
6.agentic      ─ 능동 검색 결정 / 쿼리 재작성 / 충분성 평가
       ↓
7.local_model  ─ Ollama / HuggingFace 로 비용 없는 RAG
       ↓
8.web_app      ─ Flask 풀스택 — MVP → 출처/점수 → 파일 관리 → REST API
```

## 폴더별 예제 상세

### `1.basics/` — RAG 의 출발

| 파일 | 설명 |
|---|---|
| `1.1_embeddings_intro.py` | 임베딩이란? 문장 → 1536d 벡터 + 코사인 유사도 시연 |
| `1.2_inmemory_vectorstore.py` | `InMemoryVectorStore` 로 가장 단순한 검색 |
| `1.3_first_rag.py` | 1.2 확장 — `similarity_search` → 컨텍스트 조립 → `prompt + llm` = 가장 단순한 RAG |
| `1.4_rag_chain.py` | retriever → LCEL 체인 (`RunnablePassthrough`) = 최초의 RAG 체인 |

### `2.loaders/` — 텍스트 / PDF 로딩

| 파일 | 설명 |
|---|---|
| `2.1_text_loader.py` | `TextLoader` 기본 + 자동 메타데이터 |
| `2.2_pdf_loader.py` | `PyPDFLoader` — 페이지 단위 Document |
| `2.3_chunking.py` | Character vs Recursive vs token 기반 비교 |
| `2.4_metadata.py` | source / chunk_id 부착해 출처 추적 |

### `3.vectorstore/` — Chroma 영속화  ([폴더별 상세 README](3.vectorstore/README.md))

| 파일 | 설명 |
|---|---|
| `3.1_persist.py` | persist_directory 저장/로드 (txt) — 재실행 시 비용 0 |
| `3.2_persist_pdf.py` | 같은 영속화 흐름, 로더만 `PyPDFLoader` 로 교체 (pdf) |
| `3.3_inspect.py` | DB 내부 살펴보기 (count / sample) |
| `3.4_search_modes.py` | similarity / with_score / MMR 비교 |
| `3.5_multi_collection_sep.py` | **분리(sep)** — 파일마다 컬렉션 분리 + 통합 검색(merge) |
| `3.6_single_collection_unified.py` | **통합(unified)** — 여러 파일(txt 2~3개, txt+pdf)을 한 컬렉션에 같이 → 검색 한 번에 |
| `3.7_mixed_sources.py` | **혼합(mixed)** — txt 2개(한 컬렉션) + pdf 2개(각각 별도) → 통합+분리 섞은 배치 |
| `3.8_search_scope.py` | **검색** — 통합 vs 분리일 때 검색 차이 (top-k 가 통합인지 각각인지 + filter) |
| `3.9_cross_document.py` | 정답이 A·B 문서에 쪼개져 있어도 한 컬렉션 + 넉넉한 k 면 둘 다 끌려와 종합됨 |
| `3.10_faiss_compare.py` | FAISS 비교 — 왜 Chroma 가 학습 / 일반 실무 RAG 에 더 매끄러운지 체감 |

### `4.rag_chain/` — 표준 RAG 체인

| 파일 | 설명 |
|---|---|
| `4.1_standard_chain.py` | LCEL 표준형 — `RunnablePassthrough.assign` |
| `4.2_with_citations.py` | 답변 끝에 출처 자동 부착 |
| `4.3_builtin_chains.py` | `create_retrieval_chain` 빌트인 사용 |

### `5.conversational/` — 대화형 RAG

| 파일 | 설명 |
|---|---|
| `5.1_followup_problem.py` | "그게 뭐야?" 후속 질문이 실패하는 문제 시연 |
| `5.2_history_aware_retriever.py` | LLM 으로 쿼리 재작성 → 정확한 검색 |
| `5.3_full_conversational_rag.py` | 세션 메모리 + history-aware RAG 결합 |

### `6.agentic/` — 능동 검색 (점진 빌드업)

| 파일 | 설명 |
|---|---|
| `6.1_agentic_rag.py` | (기본) 에이전트가 '검색할지 말지' 판단 — LangGraph 없이 if 분기 |
| `6.2_agentic_rag_loop.py` | (확장) + 쿼리 재작성 / 충분성 평가 / 재시도 — 평범한 for/break 루프 |
| `6.3_agentic_rag_langgraph.py` | (고도화) 6.2 와 같은 로직을 LangGraph 그래프로 재구성 (9.langgraph 예고편) |

### `7.local_model/` — 비용 없는 RAG

#### `1.ollama/`
| 파일 | 설명 |
|---|---|
| `1_chat_basic.py` | `ChatOllama` 기본 — OpenAI 와 같은 인터페이스 |
| `2_rag.py` | RAG 체인의 LLM 만 Ollama 로 교체 |
| `3_embeddings.py` | `OllamaEmbeddings` — 완전 오프라인 RAG |

#### `2.huggingface/`  (인기 모델 + 한국어 특화)
| 파일 | 설명 / 사용 모델 |
|---|---|
| `1_chat_basic.py` | `HuggingFacePipeline` — Phi-3.5-mini-instruct (또는 Qwen 2.5) |
| `2_embeddings.py` | 영어 / 다국어 / 한국어 임베딩 비교 — all-MiniLM, bge-m3, ko-sroberta |
| `3_full_rag.py` | HF LLM + HF 임베딩 — 완전 로컬 RAG |
| `4_korean_rag.py` | 한국어 특화 조합 — EXAONE-3.5 + ko-sroberta-multitask |

**자주 쓰는 모델 가이드:**

| 종류 | 모델 | 크기 | 특징 |
|---|---|---|---|
| LLM (영어) | `microsoft/Phi-3.5-mini-instruct` | ~3.8B | 작고 똑똑, 영어 ↑ |
| LLM (다국어) | `Qwen/Qwen2.5-1.5B-Instruct` | ~1.5B | 가벼움, 한국어 가능 |
| LLM (한국어) | `LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct` | ~2.4B | LG AI, 한국어 강함 |
| 임베딩 (영어) | `sentence-transformers/all-MiniLM-L6-v2` | ~22MB | 가장 가볍고 인기 |
| 임베딩 (다국어 SOTA) | `BAAI/bge-m3` | ~2.3GB | 다국어 최고 품질 |
| 임베딩 (한국어) | `jhgan/ko-sroberta-multitask` | ~470MB | 한국어 특화, 인기 |

### `8.web_app/` — Flask 풀스택 (점진 빌드업)

같은 변수/함수 이름을 유지하며 단계마다 기능을 더함 → diff 로 차이 한눈에.

| 단계 | 추가된 기능 | 포트 |
|---|---|---|
| `1.minimal/` | MVP — 업로드 + 질문 (한 파일에 다) | 5001 |
| `2.with_score/` | + 점수 + 출처 + 로딩 스피너 + `services/` 모듈화 | 5002 |
| `3.file_manage/` | + 파일 목록 + 삭제 (벡터까지 함께) — 템플릿(HTML) 버전 | 5003 |
| `4.file_manager_restapi/` | 같은 기능을 **템플릿 엔진 없이 REST API + 최소 GUI(정적 HTML)** 로 — 3단계 빌드업 | 5004 |

`1~3` 각 폴더 구조 (템플릿 버전):
```
N.이름/
├── app.py                    Flask 진입점
├── services/  (#2~)          vectorstore.py / qa_service.py
├── templates/index.html
└── static/style.css
```

`4.file_manager_restapi/` 구조 (템플릿 엔진 X — 백엔드는 JSON REST, 화면은 정적 HTML):
```
4.file_manager_restapi/
├── app.py                    1단계 — / 가 index.html 서빙 + 업로드/목록/질문 API
├── app2_delete.py            2단계 — / 가 index2_delete.html + DELETE 라우트 (app.py 유지 + 추가만)
├── app3_select.py            3단계 — / 가 index3_select.html + /ask 가 sources 로 검색 범위 한정
├── static/
│   ├── index.html            1단계 GUI — 업로드 + 질문 (fetch 로 REST 호출)
│   ├── index2_delete.html    2단계 GUI — + 파일 목록 + 삭제 버튼
│   └── index3_select.html    3단계 GUI — + 문서 체크박스 (선택한 문서 안에서만 질문)
└── services/                 vectorstore.py / qa_service.py (3.file_manage 와 동일 재사용)
```
> REST 엔드포인트: `POST /files` 업로드 · `GET /files` 목록 · `POST /ask` 질문 · `DELETE /files/<name>` 삭제(2단계~).
> `POST /ask` 는 3단계부터 `{"question": ..., "sources": ["a.pdf", ...]}` 형태로 검색 대상 문서 한정 (없으면 전체).
> `render_template`/Jinja 없이 `send_from_directory` 로 정적 HTML 만 서빙 → 데이터는 전부 fetch+JSON.
> `curl` / 모바일 앱 등 다른 클라이언트로도 같은 API 를 그대로 호출 가능.

## 자주 묻는 질문 (FAQ)

**Q. ChromaDB 가 디스크에 임베딩을 저장한다는데, 재실행 시 어떻게 안 다시 만들지?**
→ `persist_directory` 같은 경로 + 같은 `collection_name` 이면 자동으로 로드. (3.1 참고)

**Q. 검색은 잘 되는데 답이 엉뚱하다?**
→ 청크 크기 / overlap / k 값 조절. 2.3, 3.4 참고.

**Q. 후속 질문 "그거 뭐야?" 가 안 잡혀요.**
→ 5.conversational 참고. history-aware retriever 가 LLM 으로 쿼리를 재작성합니다.

**Q. OpenAI 비용 부담 없이 RAG 하고 싶어요.**
→ 7.local_model. Ollama 가 가장 간단, HuggingFace 가 모델 선택 폭이 넓음.

**Q. 한국어 데이터에 영어 임베딩을 쓰면?**
→ 품질이 떨어집니다. ko-sroberta-multitask 또는 bge-m3 를 사용하세요 (7.huggingface/2).

## 설치 & 실행

```bash
# 기본
pip install langchain langchain-openai langchain-community langchain-chroma \
            pypdf python-dotenv tiktoken

# 7.local_model — Ollama
pip install langchain-ollama
# + Ollama 데몬 설치 (https://ollama.com)
# + ollama pull llama3.2:3b
# + ollama pull nomic-embed-text     # 임베딩까지 로컬할 경우

# 7.local_model — HuggingFace
pip install langchain-huggingface transformers torch accelerate sentence-transformers

# 8.web_app
pip install flask
```

각 서브 폴더에서 실행:
```bash
cd "2.langchain/7.RAG/1.basics"
python 1.1_embeddings_intro.py

cd "../8.web_app/1.minimal"
python app.py   # → http://localhost:5001
```

## 관련 폴더

- [`../2.prompts/`](../2.prompts/) — RAG 프롬프트는 보통 system+context+question 구성
- [`../3.structured_output/`](../3.structured_output/) — 검색 결과를 구조화하고 싶을 때
- [`../4.chaining/`](../4.chaining/) — `RunnablePassthrough` 가 RAG 체인 구성 핵심
- [`../6.memory/`](../6.memory/) — RAG + 메모리 결합 (5.conversational 이 활용)
- [`../8.agents/`](../8.agents/) — Agentic RAG 는 에이전트 패턴의 한 응용
- [`../9.langgraph/`](../9.langgraph/) — Agentic RAG / 복잡한 흐름은 LangGraph
