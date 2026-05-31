"""
통합(unified) — 여러 소스를 '나누지 않고' 한 컬렉션에 합치기.
이 예제: txt 2~3개, 또는 txt+pdf 를 같은 컬렉션에 같이 적재. 종류가 달라도
한 컬렉션에 넣으면 검색 한 번에 전부 후보가 됩니다.

3.5_multi_collection_sep 과 짝 (정반대 배치):
  - 3.5 (sep)     : 파일마다 컬렉션 분리 → 검색도 따로 (격리)
  - 3.6 (unified) : 파일이 몇 개든 한 컬렉션 → 검색 한 번에 통합. 출처는 metadata.source 로 구분

언제 쓰나:
  - 문서들이 한 주제로 묶여 "항상 같이 검색" 되길 원할 때 (실무 RAG 의 기본형)
  - "특정 파일만" 골라 검색하고 싶으면? → 3.8_search_scope 의 filter 참고
"""

import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "combined"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
splitter   = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# 같이 넣을 파일들 — txt 여러 개에 pdf 가 섞여도 OK
FILES = [
    "../DATA/nvme.txt",
    "../DATA/ssd.txt",
    "../DATA/하계학술대회(CISC-S'24) CFP v2.pdf",
]


def load_any(path: str):
    """확장자로 로더 자동 선택 — .pdf 면 PyPDFLoader, 그 외엔 TextLoader"""
    if path.lower().endswith(".pdf"):
        return PyPDFLoader(path).load()
    
    return TextLoader(path, encoding="utf-8").load()


def build():
    """여러 파일을 모두 청킹해 한 컬렉션에 적재 (출처 태그 부착)"""
    chunks = []
    for path in FILES:
        part = splitter.split_documents(load_any(path))
        for c in part:
            c.metadata["source"] = os.path.basename(path)   # 출처 구분의 핵심
        chunks += part
    
    return Chroma.from_documents(
        chunks, embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )


# 이미 있으면 로드, 없으면 새로 적재
store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=PERSIST_DIR)
if store._collection.count() == 0:
    store = build()
print(f"'{COLLECTION_NAME}' 컬렉션: {store._collection.count()} 청크 (여러 파일 통합)\n")

# 검색 한 번이 모든 파일을 후보로 봄 — 결과의 source 가 제각각인 것 확인
for d in store.similarity_search("저장장치 인터페이스 속도", k=4):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")

# 포인트:
#   - 종류(txt/pdf) 상관없이 한 컬렉션 → 검색 한 번에 통합
#   - 출처 구분은 metadata['source'] 로 (안 붙이면 어느 파일에서 왔는지 알 수 없음)
#   - "특정 파일만" 검색하려면 filter 사용 → 3.8_search_scope 참고
