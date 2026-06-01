"""
표준 LCEL RAG 체인 — RunnablePassthrough.assign 으로 깔끔하게.
이 예제: 1.basics/1.3 의 RAG 를 LCEL 의 표준형으로 다시 짭니다.

핵심 차이: dict 직접 만들기 대신 RunnablePassthrough.assign 사용
  → 입력 question 을 보존하면서 검색 결과를 context 키로 자연스럽게 추가
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

# 1) 벡터 스토어 (3.vectorstore 와 동일 패턴)
PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "rag_chain_demo"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

if store._collection.count() == 0:
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load() \
         + TextLoader("../DATA/ssd.txt",  encoding="utf-8").load()
    
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    
    store.add_documents(chunks)

retriever = store.as_retriever(search_kwargs={"k": 3})


# 2) LLM + 프롬프트
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",
        "당신은 문서 기반 QA 시스템입니다. 아래 문서만 참고해서 답하세요. "
        "문서에 없으면 '모르겠습니다'라고 답하세요.\n\n문서:\n{context}"),
    ("user", "{question}"),
])


# 3) 표준형 RAG 체인 — Passthrough.assign 으로 context 추가
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

def debug_prompt(prompt_value):
    print("\n========== LLM INPUT ==========\n")
    for msg in prompt_value.messages:
        print(f"[{msg.type.upper()}]")
        print(msg.content)
        print()
    print("========== END ==========\n")
    return prompt_value

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt
    | RunnableLambda(debug_prompt)    # <-- 중간 결과 출력
    | llm
    | StrOutputParser()
)


# 4) 실행 — 입력은 {"question": ...}
print(chain.invoke({"question": "NVMe 와 SATA SSD 의 차이?"}))
