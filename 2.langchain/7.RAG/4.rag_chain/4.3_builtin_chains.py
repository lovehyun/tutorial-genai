"""
LangChain 빌트인 RAG 체인 — create_retrieval_chain + create_stuff_documents_chain.
이 예제: 4.1 에서 직접 짠 체인을 LangChain 의 빌트인으로 한 줄짜리에 가깝게.

  - create_stuff_documents_chain(llm, prompt) : 문서들을 prompt 의 {context} 에 자동 stuff
  - create_retrieval_chain(retriever, ...)    : retriever 결과를 위에 자동 연결

직접 짤 때보다 짧지만, 내부 동작이 가려져 있어 처음엔 4.1 의 직접 형 먼저 익히는 게 좋음.
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

# (벡터 스토어 준비 — 4.1 과 동일)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="rag_chain_demo",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
if store._collection.count() == 0:
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load() \
         + TextLoader("../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)
retriever = store.as_retriever(search_kwargs={"k": 3})


# 1) prompt — {context}, {input} 두 키 필수
#   ※ create_retrieval_chain 의 입력 키는 "input" (question 아님!)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 문서 기반 QA 시스템입니다. 아래 문서만 참고해 답하세요.\n\n문서:\n{context}"),
    ("user", "{input}"),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2) 문서들을 prompt 에 stuff 해서 LLM 호출하는 부분 체인
doc_chain = create_stuff_documents_chain(llm, prompt)

# 3) retriever + doc_chain 결합
rag_chain = create_retrieval_chain(retriever, doc_chain)


# 4) 실행 — 입력 키는 "input", 출력은 dict (answer + context + input)
result = rag_chain.invoke({"input": "NVMe 와 SATA SSD 의 차이?"})

print(f"질문:  {result['input']}")
print(f"답변:  {result['answer']}\n")
print(f"검색된 문서 수: {len(result['context'])}")
for d in result["context"]:
    print(f"  → {d.metadata.get('source')}: {d.page_content[:50]}...")
