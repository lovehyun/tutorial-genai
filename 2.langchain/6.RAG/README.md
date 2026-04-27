# RAG (Retrieval-Augmented Generation) 예제

LangChain을 활용한 RAG 파이프라인 구축 예제 모음입니다.

## 예제 목록

### 기초
| 파일 | 설명 |
|------|------|
| `1.storeandretrieve.py` | 기본 문서 저장 및 검색 |
| `1.storeandretrieve2_cli_history.py` | CLI 히스토리 버전 |
| `2.contentloader.py` | 텍스트 파일 로딩 |
| `2.contentloader2_source.py` | 소스 정보 포함 로딩 |
| `3.chromadb_saveload.py` | ChromaDB 저장/로드 |
| `3.chromadb2_saveload_multifiles.py` | 멀티파일 저장/로드 |

### 중급
| 파일 | 설명 |
|------|------|
| `4.pdfloader.py` | PDF 문서 로딩 |
| `4.pdfloader2_source.py` | PDF 소스 저장/로드 |
| `5.pdfloader3_saveload.py` | PDF 저장/로드 |
| `6.chromadb_search.py` | ChromaDB 검색 |
| `6.chromadb2_search_cli.py` | ChromaDB CLI 검색 |
| `7.contentloader3_multisource.py` | 멀티 소스 통합 검색 |

### 응용
| 파일 | 설명 |
|------|------|
| `9.rag_web_app/` | Flask 기반 RAG 웹 애플리케이션 |
| `10.local_model.py` | 로컬 LLM 모델 활용 |
| `11.local_model2_chunks.py` | 청크 분할 로컬 모델 |

## 설치

```bash
pip install langchain langchain-openai langchain-chroma
```

## 학습 경로

1. **기초**: 문서 로딩 → 임베딩 → 저장/검색 (1~3번)
2. **중급**: PDF 처리 → 멀티 소스 (4~7번)
3. **응용**: 웹앱 → 로컬 모델 (9~11번)
