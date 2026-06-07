"""
HuggingFace 풀 RAG — LLM 과 임베딩 모두 HF 로 (완전 오프라인).
이 예제: 4_rag_llm_only 에서 마지막 남은 OpenAI(임베딩)까지 HF 로 교체 → API 호출 0회.

  핵심 diff (4_rag_llm_only 대비): OpenAIEmbeddings → HuggingFaceEmbeddings 한 줄.

  - 임베딩: BAAI/bge-m3 (다국어 SOTA — 한국어 텍스트도 잘 잡음)
  - LLM:    microsoft/Phi-3.5-mini-instruct
  - 데이터: ../../DATA/nvme.txt + ssd.txt
"""

import os
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings, ChatHuggingFace
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1) 임베딩 — 다국어 SOTA
#    더 가벼운 옵션: "intfloat/multilingual-e5-small" (~470MB)
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# 2) 벡터 스토어 — HF 임베딩 차원이 OpenAI 와 다르므로 별도 컬렉션
store = Chroma(
    collection_name="hf_full_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_db_hf",
)
if store._collection.count() == 0:
    docs   = TextLoader("../../DATA/nvme.txt", encoding="utf-8").load() \
           + TextLoader("../../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)
    print(f"임베딩 완료 ({len(chunks)} 청크) — HF 모델 로컬 처리")
retriever = store.as_retriever(search_kwargs={"k": 3})


# 3) LLM — HuggingFacePipeline (+ ChatHuggingFace 로 chat template 적용, device_map 으로 GPU 자동)
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3.5-mini-instruct",
    task="text-generation",
    device_map="auto",
    pipeline_kwargs={"max_new_tokens": 256, "do_sample": False, "return_full_text": False},
)
chat = ChatHuggingFace(llm=llm)


# 4) RAG 체인 — 구조는 OpenAI 버전과 100% 동일
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer based on the documents below. If not in documents, say 'I don't know.'\n\nDocuments:\n{context}"),
    ("user", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt | chat | StrOutputParser()
)

print(chain.invoke({"question": "What's the difference between NVMe and SATA SSD?"}))
print("\n→ 모든 처리가 로컬. 인터넷 없이도 동작 (첫 모델 다운로드만 제외).")
