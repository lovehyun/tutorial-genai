"""
후속 질문 문제 — 단순 RAG 가 대화에서 깨지는 지점.
이 예제: "그게 뭐야?" 같은 후속 질문이 왜 안 되는지 시연합니다.

문제의 원인:
  retriever 가 보는 건 그 순간의 입력 한 문장뿐.
  "그게 뭐야?" 만으로는 무엇을 가리키는지 모르므로 엉뚱한 검색 결과를 줌.

5.2 에서 history-aware retriever 로 해결합니다.
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="conv_rag",
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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "다음 문서를 참고해 답해주세요.\n문서:\n{context}\n\n질문: {question}"
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

# 1) 첫 질문 — 잘 답함
q1 = "NVMe 가 뭐야?"
print(f"Q1: {q1}")
print(f"A1: {chain.invoke(q1)}\n")

# 2) 후속 질문 — "그거" 가 NVMe 를 가리키는 줄 모름. 검색이 엉뚱하게 됨.
q2 = "그거 PCIe 몇 세대를 쓰는데?"
print(f"Q2: {q2}")
print(f"A2: {chain.invoke(q2)}\n")
print("→ Q2 답이 어색할 가능성 큼. retriever 가 '그거' 만으로 검색했기 때문.")
print("  해결: 5.2 history-aware retriever 가 대화 맥락을 보고 쿼리를 다시 만들어줌.")
