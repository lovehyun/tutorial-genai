"""
HuggingFace 로 RAG — LLM 만 HF 로 갈아끼우기 (임베딩은 아직 OpenAI).
이 예제: 4.rag_chain/4.1_standard_chain 의 LLM 만 HuggingFace 로 교체.

핵심: 체인 구조는 그대로, ChatOpenAI → ChatHuggingFace 한 곳만 바꿈.
   (Ollama 트랙의 1.ollama/2_rag.py 와 같은 단계 — 다음 5_full_rag 에서 임베딩까지 HF 로)

준비:
  pip install langchain-huggingface transformers torch accelerate
  ※ 임베딩은 여기선 OpenAI 라 .env 의 OPENAI_API_KEY 필요.
"""

import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from langchain_openai import OpenAIEmbeddings   # ← 임베딩은 아직 OpenAI (5_full_rag 에서 교체)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 벡터 스토어 (4.rag_chain 과 동일 — 임베딩은 OpenAI)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="hf_llm_only",
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


# ─── 단 한 곳만 다름: ChatOpenAI → HuggingFacePipeline + ChatHuggingFace ───
#   device_map="auto" : GPU 있으면 GPU, 없으면 CPU. ChatHuggingFace 로 감싸 chat template 적용.
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3.5-mini-instruct",
    task="text-generation",
    device_map="auto",
    pipeline_kwargs={"max_new_tokens": 256, "do_sample": False, "return_full_text": False},
)
chat = ChatHuggingFace(llm=llm)

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
print("\n→ LLM 은 로컬(HF), 임베딩만 OpenAI. 다음(5_full_rag)에서 임베딩까지 HF 로 = 완전 오프라인.")
