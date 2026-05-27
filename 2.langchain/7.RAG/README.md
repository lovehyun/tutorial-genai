# RAG (Retrieval-Augmented Generation)

LLM 응답에 **외부 문서 검색 결과를 반영**하여 정확도를 높이는 패턴.

## 폴더 구조

```
7.RAG/
├── DATA/                     ← 공통 데이터 (여러 서브폴더에서 사용)
│   ├── nvme.txt
│   ├── ssd.txt
│   └── Python_시큐어코딩_가이드(2023년_개정본).pdf
├── chroma_db/                ← 공통 벡터 DB (예제 실행 시 생성)
│
├── 1.basics/                 ← In-memory store/retrieve 기본
├── 2.loaders/                ← 텍스트 / PDF 로더 + 메타데이터
├── 3.chromadb/               ← 벡터스토어 영속화 (저장/로드/검색)
├── 4.local_model/            ← 로컬 LLM 모델 사용
├── 5.agentic/                ← Agentic RAG (능동 검색)
├── 6.web_app/                ← 풀스택 Flask 앱 (자체 DATA/chroma_db 보유)
└── README.md
```

> **데이터 공유 정책**
> - `DATA/`, `chroma_db/` 는 **여러 서브폴더 스크립트가 공유**하므로 7.RAG 루트에 둠
> - 각 서브폴더의 스크립트는 **`../DATA/...` / `../chroma_db`** 로 상위에서 참조
> - `6.web_app/` 은 자체 데이터/벡터스토어가 있어 독립적

## 학습 흐름

```
1.basics      ─ 메모리 안에서 문서 저장/검색 (가장 단순)
       ↓
2.loaders     ─ 실제 파일(txt/PDF)에서 문서 로딩
       ↓
3.chromadb    ─ 벡터스토어에 영속화 — 재실행해도 임베딩 유지
       ↓
4.local_model ─ OpenAI 대신 로컬 모델 (오프라인/비용 절감)
       ↓
5.agentic     ─ 에이전트가 검색을 능동적으로 판단
       ↓
6.web_app     ─ 모든 걸 묶은 풀스택 앱
```

## 폴더별 상세

### `1.basics/` — In-memory store / retrieve
| 파일 | 설명 |
|------|------|
| `1.1_storeandretrieve.py` | 메모리 안에서 문서 저장 + 유사도 검색 (가장 단순) |
| `1.2_storeandretrieve_cli_history.py` | CLI + 대화 이력 |

### `2.loaders/` — 텍스트 / PDF 로더
| 파일 | 설명 |
|------|------|
| `2.1_textloader.py` | `TextLoader` 로 .txt 파일 읽기 |
| `2.2_textloader_source.py` | 출처 메타데이터 부착 (어느 파일/청크에서 왔는지) |
| `2.3_pdfloader.py` | `PyPDFLoader` 로 PDF 파일 읽기 |
| `2.4_pdfloader_source.py` | PDF + 페이지/소스 메타데이터 |

### `3.chromadb/` — 벡터스토어 영속화
| 파일 | 설명 |
|------|------|
| `3.1_save_text_single.py` | 단일 txt → ChromaDB 저장 |
| `3.2_save_text_multi.py` | 여러 txt → ChromaDB 저장 |
| `3.3_save_pdf.py` | PDF → ChromaDB 저장 |
| `3.4_search.py` | 저장된 ChromaDB 에서 검색 |
| `3.5_search_cli.py` | 대화형 CLI 검색기 |
| `3.6_multisource.py` | 여러 소스 통합 검색 + LLM 응답 |

### `4.local_model/` — 로컬 LLM 사용
| 파일 | 설명 |
|------|------|
| `4.1_basic.py` | OpenAI 대신 로컬 모델로 RAG (예: Ollama) |
| `4.2_with_chunks.py` | 청크 분할 + 로컬 모델 |

### `5.agentic/` — 능동 검색 RAG
| 파일 | 설명 |
|------|------|
| `5.1_agentic_rag.py` | 에이전트가 "검색 필요한지" 스스로 판단, 쿼리 재작성, 결과 충분성 평가 |

### `6.web_app/` — 풀스택 Flask 앱
| 파일/폴더 | 설명 |
|---------|------|
| `app.py` ~ `app4_*.py` | 점진적으로 발전하는 RAG 웹 앱 |
| `services/` | 벡터스토어 추상화 (vectorstore.py 등) |
| `static/`, `DATA/`, `chroma_db/` | 자체 정적 파일 / 데이터 / 벡터 DB |
| `debug_chroma.py` | ChromaDB 상태 검사 유틸 |

## Agentic RAG 핵심 (5.agentic/)

기존 RAG 는 항상 "질문 → 검색 → 응답" 고정 파이프라인. Agentic RAG 는 에이전트가 **검색 전략을 능동 결정**:

| 비교 | 기존 RAG | Agentic RAG |
|------|---------|-------------|
| 검색 여부 | 항상 | 필요할 때만 |
| 쿼리 | 사용자 입력 그대로 | LLM 이 재작성 |
| 검색 결과 | 그대로 사용 | 충분성 평가 후 재검색 가능 |
| 흐름 | 고정 | 적응적 루프 |

```
질문 → 검색 필요? ──No──→ 직접 응답
         │ Yes
         ↓
   쿼리 재작성 → 검색 → 충분한가? ──Yes──→ 응답
                       │ No
                       └── 재작성 (최대 N회)
```

## 관련 폴더

- [`../2.prompts/`](../2.prompts/) — RAG 프롬프트는 보통 system+context+question 구성
- [`../3.structured_output/`](../3.structured_output/) — 검색 결과를 구조화하고 싶을 때
- [`../4.chaining/`](../4.chaining/) — `RunnablePassthrough` 가 RAG 체인 구성 핵심
- [`../6.memory/`](../6.memory/) — RAG + 대화 메모리 결합 (multi-turn RAG)
- [`../8.agents/`](../8.agents/) — Agentic RAG 는 에이전트 패턴

## 설치 & 실행

```bash
pip install langchain langchain-openai langchain-community langchain-chroma pypdf python-dotenv

# 서브폴더의 스크립트는 ../DATA / ../chroma_db 를 참조하므로,
# 7.RAG 루트가 아니라 해당 서브폴더에서 실행해야 함
cd "2.langchain/7.RAG/1.basics"
python 1.1_storeandretrieve.py
```
