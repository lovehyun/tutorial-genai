# services/qa_service.py
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from services.vectorstore3 import get_vector_store

# 1. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_template("""
당신은 문서 기반 질문 응답 시스템입니다.
다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.

문서:
{context}

질문:
{question}

답변:
""")

prompt2 = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 문서 기반 질문 응답 시스템입니다."
     "다음 문서를 참고하여 사용자의 질문에 답변해 주세요."
     "문서에 답변할 내용이 없으면 반드시 '모르겠습니다'라고 답하세요.\n\n"
     "문서:\n{context}\n"),
    ("human", "{question}")
])

# 2. LLM 준비 (gpt-3.5-turbo 기반)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 3. 출력 파서
output_parser = StrOutputParser()

# 4. 체인 생성
chain = prompt | llm | output_parser

def answer_question(question: str) -> str:
    store = get_vector_store()
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    docs = store.similarity_search(question, k=5)
    context = "\n\n".join(d.page_content for d in docs)
    
    try:
        result = chain.invoke({"context": context, "question": question})
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"
    return f"질문: {question}\n응답: {result.strip()}"


def answer_question_score(question: str) -> str:
    store = get_vector_store()
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    # 1. 벡터 DB에서 유사 문서 검색 (점수 포함)
    docs_with_scores = store.similarity_search_with_score(question, k=5)

    # 2. context 구성
    # context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
    context = "\n\n".join(
        [f"[문서 {i+1}] (유사도 {round((1 - score) * 100, 2)}%)\n{doc.page_content}"
        for i, (doc, score) in enumerate(docs_with_scores)]
    )
    print(context)
    
    # 3. LLM 체인 실행
    try:
        result = chain.invoke({"context": context, "question": question})
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"

    # 4. 출처 문서 + 유사도 정보 추출
    source_lines = []
    for doc, score in docs_with_scores:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        page = int(doc.metadata.get("page", 0)) + 1
        score_percent = round((1 - score) * 100, 2)  # 유사도는 낮을수록 가까움 → 반전
        source_lines.append(f"{source} (page {page}, 유사도 {score_percent}%)")

    # 5. 최종 출력
    return (
        f"질문: {question}\n"
        f"응답: {result.strip()}\n"
        f"참고 문서:\n" + "\n".join(f" - {line}" for line in source_lines)
    )
