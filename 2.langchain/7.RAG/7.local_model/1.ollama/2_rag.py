"""
Ollama 로 RAG — LLM 만 로컬로 갈아끼우기 (임베딩은 아직 OpenAI).
이 예제: 4.rag_chain/4.1_standard_chain 의 LLM 만 ChatOllama 로 교체.

핵심: 체인 구조는 그대로, ChatOpenAI → ChatOllama 한 줄만 바꿈.
   다음(3_embeddings)에서 임베딩까지 로컬화하면 완전 오프라인 RAG.
"""
# pip install langchain_ollama

import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_openai import OpenAIEmbeddings   # ← 임베딩은 아직 OpenAI (3_embeddings 에서 교체)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

# 벡터 스토어 (4.rag_chain 과 동일)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="ollama_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

if store._collection.count() == 0:
    docs   = TextLoader("../../DATA/nvme.txt", encoding="utf-8").load() \
           + TextLoader("../../DATA/ssd.txt",  encoding="utf-8").load()

    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)

    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))

    store.add_documents(chunks)

retriever = store.as_retriever(search_kwargs={"k": 3})

# ─── 단 한 줄만 다름: ChatOpenAI → ChatOllama ───
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

print(chain.invoke({"question": "NVMe 와 SATA SSD 의 차이?"}))
