"""
벡터 스토어 서비스 — #3 의 도메인 로직을 services/ 모듈로 분리(리팩토링).

#4 의 의미:
  - 기능: #3(누적/목록/삭제) 을 그대로 유지
  - 구조: app.py 에 몰려 있던 로직을 services/ 로 분리(구조화 리팩토링)
  - 추가: 점수 검색(search_with_score) 으로 답변에 출처/유사도 표시 가능하게

여기(vectorstore.py)는 "벡터 DB 와 문서"에 관한 모든 일을 담당한다:
  add_pdf / list_documents / delete_document / search_with_score
app.py 는 이 함수들을 호출만 하는 얇은 컨트롤러가 된다.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

DATA_DIR        = "../DATA"         # 1~5 공유 (= 8.web_app/DATA)
PERSIST_DIR     = "../chroma_db"    # 벡터 DB 도 8.web_app 안에서 공유
COLLECTION_NAME = "rag_web"

os.makedirs(DATA_DIR, exist_ok=True)

# persist_directory 를 주면, 이 객체를 만드는 순간 디스크의 기존 문서를 로드한다.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)


def _distinct_sources() -> dict:
    """벡터 DB 안의 문서별 청크 수를 {파일명: 청크수} 로 집계."""
    data = store._collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for m in data.get("metadatas", []):
        src = (m or {}).get("source", "(unknown)")
        counts[src] = counts.get(src, 0) + 1
    return counts


def list_documents() -> list[dict]:
    """벡터 DB 에 들어있는 문서 목록 (파일명 + 청크 수)."""
    return [{"source": s, "chunks": c}
            for s, c in sorted(_distinct_sources().items())]


def add_pdf(file_path: str) -> dict:
    """PDF 를 청킹해서 벡터 DB 에 추가. 이미 있는 문서면 건너뜀."""
    source = os.path.basename(file_path)
    if source in _distinct_sources():
        return {"source": source, "added": False}

    docs = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = source
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)
    return {"source": source, "added": True}


def delete_document(source: str) -> bool:
    """문서 1건 삭제 — 해당 source 의 벡터 청크를 제거.

    (#3 과 동일하게 원본 PDF 파일은 보존한다. 원본까지 지우려면 아래 주석 해제.)
    """
    existed = source in _distinct_sources()
    store._collection.delete(where={"source": source})

    # 원본 파일까지 삭제하려면:
    # path = os.path.join(DATA_DIR, source)
    # if os.path.exists(path):
    #     os.remove(path)

    return existed


def is_empty() -> bool:
    return store._collection.count() == 0


def search_with_score(question: str, k: int = 5):
    """점수와 함께 검색 — #4 차등: 출처/유사도 표시에 사용."""
    return store.similarity_search_with_score(question, k=k)
