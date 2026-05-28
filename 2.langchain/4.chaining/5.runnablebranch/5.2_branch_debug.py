"""
RunnableBranch — 조건 함수 결과에 따라 다른 체인으로 라우팅하는 Runnable.
이 예제: 각 체인 앞에 RunnableLambda print 를 끼워 "어느 분기를 탔는지" 추적합니다.

각 체인 앞에 RunnableLambda 를 끼워 "어느 분기를 탔는지" 콘솔에 출력합니다.

테스트 질문 중 "된장찌개 파이썬 레시피"는 두 조건에 모두 매칭됩니다.
→ RunnableBranch 는 위에서부터 평가하므로 먼저 매칭되는 코드 분기로 갑니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


def make_chain(role):
    return (
        ChatPromptTemplate.from_messages([
            ("system", role),
            ("user", "{question}"),
        ])
        | llm
        | StrOutputParser()
    )


# 각 체인 앞에 진입 로그를 찍는 RunnableLambda 끼우기
code_chain = (
    RunnableLambda(lambda x: print(">>> 개발자 체인 진입") or x)
    | make_chain("당신은 파이썬 개발자입니다.")
)
cook_chain = (
    RunnableLambda(lambda x: print(">>> 요리사 체인 진입") or x)
    | make_chain("당신은 요리 전문가입니다.")
)
general_chain = (
    RunnableLambda(lambda x: print(">>> 일반 체인 진입") or x)
    | make_chain("당신은 일반 어시스턴트입니다.")
)

branch = RunnableBranch(
    (lambda x: "파이썬" in x["question"] or "코드" in x["question"], code_chain),
    (lambda x: "요리" in x["question"] or "레시피" in x["question"], cook_chain),
    general_chain,
)

questions = [
    # "파이썬 리스트 정렬 코드 알려줘",
    # "김치찌개 레시피 알려줘",
    # "오늘 날씨 어때?",
    "된장찌개 파이썬 레시피 알려줘",   # ← 두 조건 모두 매칭. 위쪽이 이긴다.
]

for q in questions:
    print("질문:", q)
    print("답변:", branch.invoke({"question": q}))
    print("-" * 60)
