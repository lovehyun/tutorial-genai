"""
RunnableBranch — 조건 함수 결과에 따라 다른 체인으로 라우팅하는 Runnable.
이 예제: 질문 복잡도를 분류기로 판정해 저가/고가 모델로 자동 라우팅합니다.

운영 비용 최적화의 전형 패턴.
  쉬운 질문  → gpt-4o-mini   (싸고 빠름)
  어려운 질문 → gpt-4o       (정확하지만 비쌈)

  ※ 분류는 저렴한 모델로만 한 번 — 분류 비용을 답변 절감 효과보다 작게 유지.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

load_dotenv()

# 두 모델 — 가격/품질이 다름
cheap_llm  = ChatOpenAI(model="gpt-4o-mini", temperature=0)
strong_llm = ChatOpenAI(model="gpt-4o",      temperature=0)


# 1단계: 분류기 (저렴한 모델로 복잡도만 판정)
classifier = (
    ChatPromptTemplate.from_template(
        "다음 질문의 난이도를 'easy' 또는 'hard' 한 단어로만 답해.\n"
        "easy : 단순 사실/정의/한 줄 답으로 충분.\n"
        "hard : 추론/코드 작성/긴 분석이 필요.\n"
        "질문: {question}"
    )
    | cheap_llm
    | StrOutputParser()
)


# 2단계: 두 갈래 답변 체인
def make_answer_chain(model):
    return ChatPromptTemplate.from_template("{question}") | model | StrOutputParser()

cheap_chain  = make_answer_chain(cheap_llm)
strong_chain = make_answer_chain(strong_llm)


# 분류 + 사용된 모델 이름 + 답변을 같은 dict 에 담아 반환
chain = (
    RunnablePassthrough.assign(complexity=classifier)
    | RunnablePassthrough.assign(
        model_used=lambda x: "gpt-4o-mini" if "easy" in x["complexity"].lower() else "gpt-4o",
        answer=RunnableBranch(
            (lambda x: "easy" in x["complexity"].lower(), cheap_chain),
            strong_chain,  # default = hard
        ),
    )
)

questions = [
    "파이썬의 print 함수는 무엇인가요?",
    "버블 정렬을 구현하고, 시간 복잡도와 더 효율적인 대안을 비교 분석해줘.",
    "오늘은 무슨 요일?",
]

for q in questions:
    print("=" * 60)
    print(f"[질문]   {q}")
    result = chain.invoke({"question": q})
    print(f"[난이도] {result['complexity'].strip()}  →  사용 모델: {result['model_used']}")
    answer = result["answer"]
    print(f"[답변]   {answer[:200]}{'...' if len(answer) > 200 else ''}")
