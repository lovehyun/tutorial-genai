"""
OllamaEmbeddings — 임베딩까지 로컬로. 완전 오프라인 RAG.
이 예제: 임베딩 + LLM 모두 Ollama. OpenAI API 호출 0회.

준비:
  ollama pull nomic-embed-text   # 임베딩 모델 (~270MB)
  ollama pull llama3.2:3b        # LLM (이미 받았다면 생략)

장점: 비용 0, 데이터 외부 유출 X, 오프라인.
단점: OpenAI 임베딩보다 다국어 품질 살짝 ↓ 가능.
"""

import os

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# ─── 임베딩도 로컬 — OpenAIEmbeddings → OllamaEmbeddings ───
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 별도 컬렉션에 저장 (OpenAI 임베딩 차원과 다르므로 섞이면 안 됨)
store = Chroma(
    collection_name="ollama_full",       # ← 새 컬렉션
    embedding_function=embeddings,
    persist_directory="./chroma_db_ollama",   # ← 별도 디렉토리
)
if store._collection.count() == 0:
    docs   = TextLoader("../../DATA/nvme.txt", encoding="utf-8").load() \
           + TextLoader("../../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)
    print(f"임베딩 완료 ({len(chunks)} 청크) — 모두 로컬 처리")
retriever = store.as_retriever(search_kwargs={"k": 3})

# LLM 도 로컬
llm = ChatOllama(model="llama3.2:3b", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 문서를 참고해 한국어로 간결히 답하세요.\n\n문서:\n{context}"),
    ("user", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt | llm | StrOutputParser()
)

print(chain.invoke({"question": "NVMe 의 인터페이스는?"}))
print("\n→ OpenAI API 호출 0회 — 모든 처리가 로컬에서.")
