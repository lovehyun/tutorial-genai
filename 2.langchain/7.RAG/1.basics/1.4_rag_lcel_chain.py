"""
첫 RAG 체인 — 검색 결과를 LLM 프롬프트에 끼워서 답변 생성.
이 예제: 검색된 문서를 컨텍스트로 LLM 에게 던져 답변을 받는 가장 단순한 RAG.

흐름:
  질문 → retriever 가 관련 문서 검색 → prompt 의 {context} 자리에 끼움 → LLM 응답

  사용자 질문
      ↓
  RunnablePassthrough
      ↓
  Retriever
      ↓
  Vector Search
      ↓
  관련 문서
      ↓
  Prompt
      ↓
  GPT-4o-mini
      ↓
  최종 답변

"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 1) 문서 + 벡터 스토어 (1.2 와 동일)
docs = [
    Document(page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다."),
    Document(page_content="SATA SSD 는 NVMe 보다 속도가 느리지만 호환성이 좋다."),
    Document(page_content="HDD 는 회전 디스크 기반이라 IO 가 느린 편이다."),
    Document(page_content="PCIe 4.0 NVMe 는 약 7GB/s 수준의 시퀀셜 속도를 낸다."),
]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
retriever = store.as_retriever(search_kwargs={"k": 2})

# 2) LLM + 프롬프트
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "다음 문서를 참고해서 질문에 답해주세요.\n\n"
    "문서:\n{context}\n\n"
    "질문: {question}"
)


def format_docs(docs):
    """검색된 Document 리스트 → 하나의 문자열"""
    return "\n\n".join(d.page_content for d in docs)

# 아래 포멧을 사용자 문장 형태로 변경
# [
#     Document(...),
#     Document(...),
#     Document(...)
# ]
# 즉,
# [
#     Document(
#         page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다."
#     ),
#     Document(
#         page_content="SATA SSD 는 NVMe 보다 속도가 느리다."
#     )
# ]
# 위 내용을 자연어로...
# 문서:
# NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다.
# SATA SSD 는 NVMe 보다 속도가 느리다.


# 3) RAG 체인: 질문 → 검색 → 컨텍스트 조립 → LLM
chain = (
    {
        "context": retriever | format_docs, 
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 4) 실행
question = "NVMe 와 SATA 의 속도 차이?"
print(f"Q: {question}")
print(f"A: {chain.invoke(question)}")


# 사용자 질문
#     │
#     ▼
# "NVMe 와 SATA 의 차이?"
#     │
#     ├──────────────► RunnablePassthrough
#     │                      │
#     │                      ▼
#     │                question
#     │
#     └──────────────► retriever
#                            │
#                            ▼
#                      Document[]
#                            │
#                            ▼
#                      format_docs
#                            │
#                            ▼
#                         context
#
#         ▼
# {
#     "context": "...",
#     "question": "..."
# }
#         ▼
#       prompt
#         ▼
#        llm
#         ▼
#       결과

# LCEL이 어려우면???
"""
# 검색
docs = retriever.invoke(query)

# 문자열 변환
context = format_docs(docs)

# 생성
answer = (
    prompt
    | llm
    | StrOutputParser()
).invoke({
    "context": context,
    "question": query
})

print(answer)
"""
