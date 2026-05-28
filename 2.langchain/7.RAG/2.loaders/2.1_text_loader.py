"""
TextLoader — 텍스트 파일을 LangChain Document 로 불러오기.
이 예제: ../DATA/nvme.txt 를 읽고, 자동으로 부여되는 메타데이터를 확인합니다.

LangChain 의 모든 RAG 입력은 Document(page_content, metadata) 입니다.


─── 자주 헷갈리는 점: 한 문장씩? 한 문서씩? ──────────────────

핵심: **Loader 단계에서는 분할(청킹) 을 하지 않습니다.**

  TextLoader        : 파일 1개 = Document 1개  (텍스트 전체가 통째로)
  PyPDFLoader (2.2) : PDF 페이지 1개 = Document 1개

  예) nvme.txt (14KB)  →  [Document(page_content="(파일 전체 14KB)")]
                          길이 1짜리 리스트. 안에 통문서가 들어 있음.

문장/청크 단위 분할은 **2.3 splitter 단계** 에서 일어납니다.
(보통 500~1000 글자/토큰 단위. 한 문장 단위는 너무 짧아 잘 안 씀.)

전체 흐름:
  원본 파일
    ↓ Loader      파일/페이지 단위 Document  (2.1, 2.2 ← 여기)
    ↓ Splitter    수백 글자/토큰 단위 청크    (2.3)
    ↓ Embedding   각 청크를 벡터화
    ↓ VectorStore 벡터+청크 저장             (3.vectorstore)
    ↓ Retriever   질문 → top-k 청크 검색
    ↓ LLM         청크들을 context 로 프롬프트에 끼움

따라서 이 파일에는 chunk_size 같은 설정이 등장하지 않습니다 (분할 단계가 아님).
"""

from langchain_community.document_loaders import TextLoader

loader = TextLoader("../DATA/nvme.txt", encoding="utf-8")
documents = loader.load()

print(f"불러온 Document 개수: {len(documents)}\n")

# Document 한 개의 구조
doc = documents[0]
print(f"page_content (앞 200자):\n{doc.page_content[:200]}...\n")
print(f"metadata: {doc.metadata}")

# TextLoader 는 파일 하나를 Document 하나로 만듭니다.
# metadata 의 'source' 는 자동으로 파일 경로가 들어갑니다.
# 다음(2.3)에서 이 Document 를 더 작은 청크로 쪼갭니다.
