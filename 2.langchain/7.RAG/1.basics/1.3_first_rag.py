from dotenv import load_dotenv

from langchain_openai import (
    OpenAIEmbeddings,
    ChatOpenAI
)

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

docs = [
    Document(page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다."),
    Document(page_content="SATA SSD 는 NVMe 보다 속도가 느리다."),
    Document(page_content="HDD 는 회전 디스크 기반이라 IO 가 느린 편이다."),
]

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

store = InMemoryVectorStore.from_documents(
    docs,
    embedding=embeddings
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

query = "NVMe 와 SATA 의 차이?"

# 검색
results = store.similarity_search(query, k=3)

# 검색 결과 합치기
context = "\n".join(
    doc.page_content
    for doc in results
)

prompt = ChatPromptTemplate.from_template("""
아래 문서를 참고하여 질문에 답변하시오.

문서:
{context}

질문:
{question}
""")

chain = prompt | llm

answer = chain.invoke({
    "context": context,
    "question": query
})

print(answer.content)
