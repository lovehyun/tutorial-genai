"""
QA 서비스 — 4.refactor_with_score 와 동일한 표준 LCEL 파이프라인.
(REST API 버전이지만 답변 생성 로직은 화면과 무관하므로 그대로 재사용)

차이점: 입력이 {question, sources} 인 dict 다. sources(선택 문서) 가 주어지면
그 문서들 안에서만 검색한다(문서 선택 검색, app3_select.py 에서 사용).
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from services.vectorstore import search_with_score, is_empty

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])


def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


# 검색 단계(교재 4.2 retrieve_and_split 패턴): {"question", "sources"} → docs + context
# sources 가 있으면 그 문서들 안에서만 검색. 유사도 점수는 metadata['score'] 에 부착.
def retrieve(inputs: dict):
    docs = []
    for doc, distance in search_with_score(inputs["question"], k=5, sources=inputs.get("sources")):
        doc.metadata["score"] = round((1 - distance) * 100, 1)
        docs.append(doc)
    return {"question": inputs["question"], "docs": docs, "context": format_docs(docs)}


# 전체 체인: 검색 → answer 를 assign
rag_chain = (
    RunnableLambda(retrieve)
    | RunnablePassthrough.assign(answer=(prompt | llm | StrOutputParser()))
)


def answer_question(question: str, sources: list[str] | None = None) -> dict:
    # sources: 검색을 한정할 파일명 리스트. None/빈 값이면 전체 문서 대상.
    if is_empty():
        return {"answer": "먼저 PDF를 업로드해주세요.", "sources": []}

    # 검색+LLM 단일 파이프라인 실행 → {question, docs, context, answer}
    result = rag_chain.invoke({"question": question, "sources": sources})
    docs = result["docs"]

    out_sources = [{
        "file":  os.path.basename(doc.metadata.get("source", "?")),
        "page":  int(doc.metadata.get("page", 0)) + 1,
        "score": doc.metadata["score"],
    } for doc in docs]

    return {"answer": result["answer"], "sources": out_sources}
