# RAG 마스터클래스

## 과정 정보
- **기간**: 3일 (총 24시간)
- **난이도**: 중급
- **대상**: LangChain 기초를 익히고 문서 기반 QA 시스템을 구축하고 싶은 개발자
- **선수 과목**: 입문 3. LangChain 핵심 마스터

## 학습 목표
1. 임베딩의 원리를 이해하고 벡터 공간을 시각화할 수 있다
2. FAISS와 ChromaDB를 사용해 벡터 저장소를 구축할 수 있다
3. PDF/텍스트 문서를 로드하고 RAG 파이프라인을 완성할 수 있다
4. RAG 웹 앱을 구축하고 Agentic RAG로 확장할 수 있다

## 커리큘럼

### Day 1: 임베딩 이론과 FAISS

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | RAG 아키텍처 개요, 환경 설정 |
| 09:30-10:00 | 토큰화 시각화 | `12.study/6.embedding/1.tokenize_visualize.py` | 텍스트가 토큰으로 변환되는 과정 시각화 |
| 10:00-10:30 | 임베딩 시각화 | `12.study/6.embedding/2.embedding_visualize.py` | 임베딩 벡터의 의미 공간 시각화 |
| 10:45-11:15 | 벡터 공간 (2D/3D) | `12.study/6.embedding/3.vector_space_2d.py`, `12.study/6.embedding/5.vector_space_3d.py` | 2D, 3D 벡터 공간에서 유사도 이해 |
| 11:15-12:00 | 유사도 행렬 | `12.study/6.embedding/4.similarity_matrix.py` | 코사인 유사도 행렬 계산 및 시각화 |
| 13:00-13:45 | FAISS 기초 | `1.openai/7.rag/1.rag_basic.py`, `1.openai/7.rag/2.rag_similarity_score.py` | FAISS 인덱스 생성, 검색 기초 |
| 13:45-14:30 | FAISS 로컬 임베딩 | `1.openai/7.rag/3.rag_local_embedding.py`, `1.openai/7.rag/4.rag_cosine_similarity.py` | 로컬 임베딩 모델 + 코사인 유사도 |
| 14:45-15:30 | FAISS 모델 비교 | `1.openai/7.rag/5.rag_better_embedding_model.py` | 다양한 임베딩 모델 성능 비교 |
| 15:30-16:15 | 로컬 모델 RAG | `2.langchain/7.RAG/7.local_model/1.ollama/2_rag.py` | 로컬 LLM + RAG 완전 로컬 파이프라인 |
| 16:15-17:00 | Day 1 정리 & Q&A | — | FAISS 실습 정리, 질의응답 |

### Day 2: ChromaDB와 RAG 파이프라인

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 임베딩, FAISS 핵심 복습 |
| 09:30-10:00 | LangChain 기본 RAG | `2.langchain/7.RAG/1.basics/1.3_first_rag.py` | Store & Retrieve 기본 패턴 |
| 10:00-10:30 | RAG + 대화 히스토리 | `2.langchain/7.RAG/5.conversational/5.3_full_conversational_rag.py` | 대화 히스토리를 포함한 RAG |
| 10:45-11:15 | 콘텐츠 로더 | `2.langchain/7.RAG/2.loaders/2.1_text_loader.py`, `2.langchain/7.RAG/2.loaders/2.5_metadata.py` | 텍스트 파일 로드, 소스 추적 |
| 11:15-12:00 | ChromaDB 저장/로드 | `2.langchain/7.RAG/3.vectorstore/3.1_persist.py`, `2.langchain/7.RAG/3.vectorstore/3.6_single_collection_unified.py` | ChromaDB 영구 저장, 다중 파일 |
| 13:00-13:45 | PDF 로더 | `2.langchain/7.RAG/2.loaders/2.2_pdf_loader.py`, `2.langchain/7.RAG/2.loaders/2.4_chunking_pdf.py` | PDF 문서 로드 및 청크 |
| 13:45-14:30 | PDF 저장/로드 & 검색 | `2.langchain/7.RAG/3.vectorstore/3.2_persist_pdf.py`, `2.langchain/7.RAG/3.vectorstore/3.4_search_modes.py` | PDF → ChromaDB 저장, 유사도 검색 |
| 14:45-15:15 | ChromaDB 검색 범위 | `2.langchain/7.RAG/3.vectorstore/3.8_search_scope.py` | 통합/분리 컬렉션 검색 범위 |
| 15:15-15:45 | 멀티소스 로더 | `2.langchain/7.RAG/3.vectorstore/3.7_txtpdf_mixed_sources.py` | 여러 소스(텍스트, PDF 등) 통합 로드 |
| 15:45-16:15 | 로컬 모델 RAG | `2.langchain/7.RAG/7.local_model/1.ollama/2_rag.py`, `2.langchain/7.RAG/7.local_model/2.huggingface/5_full_rag.py` | 로컬 LLM 기반 RAG (Ollama / HuggingFace) |
| 16:15-17:00 | Day 2 정리 & Q&A | — | ChromaDB, RAG 파이프라인 정리 |

### Day 3: RAG 웹 앱과 Agentic RAG

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | RAG 파이프라인 핵심 복습 |
| 09:30-10:00 | RAG 웹 앱 기초 | `2.langchain/7.RAG/8.web_app/1.minimal/app.py` | Flask 기반 RAG 웹 앱 (MVP) |
| 10:00-10:30 | 파일 추가 | `2.langchain/7.RAG/8.web_app/2.file_append/app.py` | 동적 문서 추가 기능 |
| 10:45-11:15 | 파일 삭제 | `2.langchain/7.RAG/8.web_app/3.file_delete/app.py` | 동적 문서 삭제 (벡터까지 함께) |
| 11:15-12:00 | 검색 스코어 & 리팩터링 | `2.langchain/7.RAG/8.web_app/4.refactor_with_score/app.py` | 유사도 점수 표시 + services/ 모듈화 |
| 13:00-13:30 | QA 서비스 구조 | `2.langchain/7.RAG/8.web_app/4.refactor_with_score/services/qa_service.py` | QA 서비스 모듈 설계 |
| 13:30-14:00 | 벡터스토어 서비스 | `2.langchain/7.RAG/8.web_app/4.refactor_with_score/services/vectorstore.py` | 벡터스토어 추상화 |
| 14:00-14:30 | REST API 버전 | `2.langchain/7.RAG/8.web_app/5.file_manager_restapi/app.py` | 템플릿 없이 순수 REST API 로 재구성 |
| 14:45-15:30 | Agentic RAG | `2.langchain/7.RAG/6.agentic/6.1_agentic_rag.py` | 에이전트가 검색을 자율 판단하는 Agentic RAG |
| 15:30-17:00 | 종합 프로젝트 | — | 나만의 문서 QA 시스템 구축, 결과 발표 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-community chromadb faiss-cpu flask pypdf
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/06_rag_system.md` | RAG 시스템 (임베딩, 벡터DB, 파이프라인) |

## 참고 자료
- `12.study/6.embedding/` — 임베딩 이론 및 시각화
- `1.openai/7.rag/` — FAISS 기초
- `2.langchain/7.RAG/` — LangChain RAG 전체
- `2.langchain/7.RAG/8.web_app/` — RAG 웹 앱 프로젝트
