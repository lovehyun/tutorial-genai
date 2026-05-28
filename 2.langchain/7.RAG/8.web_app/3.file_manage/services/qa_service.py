"""
QA 서비스 — #2 와 동일. (파일 관리는 vectorstore 에서)
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from services.vectorstore import search_with_score, is_empty

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])
chain = prompt | llm | StrOutputParser()


def answer_question(question: str) -> dict:
    if is_empty():
        return {"answer": "먼저 PDF를 업로드해주세요.", "sources": []}

    docs_scored = search_with_score(question, k=5)
    context = "\n\n".join(d.page_content for d, _ in docs_scored)
    answer = chain.invoke({"context": context, "question": question})

    sources = []
    for doc, score in docs_scored:
        sources.append({
            "file":  os.path.basename(doc.metadata.get("source", "?")),
            "page":  int(doc.metadata.get("page", 0)) + 1,
            "score": round((1 - score) * 100, 1),
        })
    return {"answer": answer, "sources": sources}
