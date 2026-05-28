"""
한국어 특화 RAG — 한국어 데이터에 최적화된 HF 모델 조합.
이 예제: 한국어 임베딩 + 한국어 LLM 으로 한국어 PDF RAG.

조합:
  - 임베딩: jhgan/ko-sroberta-multitask (한국어 특화, 가장 인기)
  - LLM:    LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct (LG AI, 한국어 강함)
            또는 Qwen/Qwen2.5-3B-Instruct (다국어, 한국어 능숙)

준비:
  pip install langchain-huggingface sentence-transformers transformers torch
  EXAONE 은 HF 에서 라이센스 동의 필요할 수 있음 — 안 되면 Qwen 으로 대체.

데이터: ../../DATA/nvme.txt (한국어 텍스트)
"""

import os
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# 1) 한국어 특화 임베딩
embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")

store = Chroma(
    collection_name="korean_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_db_korean",
)
if store._collection.count() == 0:
    docs   = TextLoader("../../DATA/nvme.txt", encoding="utf-8").load() \
           + TextLoader("../../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)
    print(f"한국어 임베딩 완료 ({len(chunks)} 청크)")
retriever = store.as_retriever(search_kwargs={"k": 3})


# 2) 한국어 LLM
#    1순위: EXAONE 3.5 2.4B (LG AI, 한국어 학습 강함)
#    대체: Qwen2.5-3B-Instruct (라이센스 동의 없이 바로 사용 가능)
LLM_ID = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
# LLM_ID = "Qwen/Qwen2.5-3B-Instruct"   # 라이센스 이슈 시 이걸로

llm = HuggingFacePipeline.from_model_id(
    model_id=LLM_ID,
    task="text-generation",
    pipeline_kwargs={
        "max_new_tokens": 300,
        "do_sample": False,
        "return_full_text": False,
    },
    model_kwargs={"trust_remote_code": True},   # EXAONE/Qwen 필요
)


# 3) RAG 체인 — 한국어 프롬프트
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서만 참고해서 한국어로 답하세요. 문서에 없는 내용은 '모르겠습니다' 라고 답하세요.\n\n"
     "문서:\n{context}"),
    ("user", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt | llm | StrOutputParser()
)

print(chain.invoke({"question": "NVMe 와 SATA SSD 의 속도 차이를 설명해줘."}))
print("\n→ 한국어 데이터 + 한국어 모델 조합으로 한국어 RAG.")
