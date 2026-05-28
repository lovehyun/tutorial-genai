"""
RunnableBranch — 조건 함수 결과에 따라 다른 체인으로 라우팅하는 Runnable.
이 예제: 키워드 매칭 한계 극복용으로 LLM 분류기에 카테고리를 판정시키고 그 결과로 분기합니다.

키워드 매칭(6.1, 6.2)은 단순한 경우엔 OK지만, "지난주에 산 물건이 아직 안왔어요"
같은 문장처럼 키워드가 약하면 잡지 못합니다.

LLM에게 먼저 카테고리를 분류시키고, 그 결과로 분기하는 패턴.
  1단계: classifier 체인 → "결제" / "배송" / "기술" / "기타"
  2단계: 분류 결과로 RunnableBranch 분기
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def make_chain(role):
    return (
        ChatPromptTemplate.from_messages([
            ("system", role),
            ("user", "{question}"),
        ])
        | llm
        | StrOutputParser()
    )


payment_chain  = make_chain("당신은 결제 상담원입니다.")
delivery_chain = make_chain("당신은 배송 상담원입니다.")
tech_chain     = make_chain("당신은 기술 지원 담당자입니다.")
general_chain  = make_chain("당신은 일반 상담원입니다.")


# 1단계: LLM 분류기 (카테고리만 한 단어로 반환)
classifier = (
    ChatPromptTemplate.from_template(
        "다음 질문의 카테고리를 한 단어로만 답해: 결제 / 배송 / 기술 / 기타.\n"
        "질문: {question}"
    )
    | llm
    | StrOutputParser()
)


# 2단계: 분류 결과 + 답변을 dict에 모두 담아 반환
chain = (
    RunnablePassthrough.assign(category=classifier)
    | RunnablePassthrough.assign(
        answer=RunnableBranch(
            (lambda x: "결제" in x["category"], payment_chain),
            (lambda x: "배송" in x["category"], delivery_chain),
            (lambda x: "기술" in x["category"], tech_chain),
            general_chain,
        )
    )
)

# 키워드만으로는 잡기 어려운 질문들
questions = [
    "지난주에 산 물건이 아직도 안왔어요.",        # 명시적 키워드 없지만 → 배송
    "두 번 청구된 것 같아요.",                   # → 결제
    "앱이 갑자기 종료돼요.",                     # → 기술
    "고객센터 운영시간이 궁금해요.",                # → 기타
]

for q in questions:
    print("=" * 60)
    print(f"[고객]   {q}")
    result = chain.invoke({"question": q})
    print(f"[분류]   {result['category'].strip()}")
    print(f"[답변]   {result['answer']}")
