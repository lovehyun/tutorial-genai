"""
QA 서비스 — answer_question 을 별도 모듈로 분리(#4 구조화 리팩토링).
이 예제: search_with_score 결과로 유사도(%) + 출처 페이지를 함께 반환.
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
    """답변 + 출처 리스트(파일, 페이지, 유사도) 를 dict 로 반환"""
    if is_empty():
        return {"answer": "먼저 PDF를 업로드해주세요.", "sources": []}

    # 점수 포함 검색
    docs_scored = search_with_score(question, k=5)

    # ── 중간 결과: RAG 검색 결과를 터미널에 출력 (유사도 포함) ──
    print(f"\n>>> [RAG] 질문: {question}")
    print(f">>> [RAG] 검색된 청크 {len(docs_scored)}개:")
    for i, (doc, score) in enumerate(docs_scored, 1):
        src = os.path.basename(doc.metadata.get("source", "?"))
        page = doc.metadata.get("page")
        page_str = f", p.{page + 1}" if isinstance(page, int) else ""
        sim = round((1 - score) * 100, 1)
        snippet = doc.page_content[:100].replace("\n", " ")
        print(f"    [{i}] {src}{page_str} (유사도 {sim}%)\n        {snippet}...")

    context = "\n\n".join(d.page_content for d, _ in docs_scored)

    answer = chain.invoke({"context": context, "question": question})

    # 출처 정보 정리
    sources = []
    for doc, score in docs_scored:
        sources.append({
            "file":  os.path.basename(doc.metadata.get("source", "?")),
            "page":  int(doc.metadata.get("page", 0)) + 1,
            "score": round((1 - score) * 100, 1),     # 거리 → 대략적 유사도(%)
        })

    return {"answer": answer, "sources": sources}
