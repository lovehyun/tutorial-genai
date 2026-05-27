"""
RunnableBranch — 조건에 따라 다른 체인으로 라우팅

질문 유형에 따라 다른 프롬프트/체인을 적용한다.
  - 코드 관련 질문   → 개발자 페르소나 체인
  - 요리 관련 질문   → 요리 전문가 체인
  - 그 외           → 일반 어시스턴트 체인 (기본값)

if/else 를 체인 안에 박는 패턴. 라우터/디스패처를 LCEL 로 구현.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# 1. 라우팅 대상 체인 3개 정의
def make_chain(system_msg):
    return (
        ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("user",   "{question}"),
        ])
        | llm
        | StrOutputParser()
    )

code_chain    = make_chain("당신은 시니어 파이썬 개발자입니다. 코드 예제 위주로 간결하게 답하세요.")
cooking_chain = make_chain("당신은 요리 전문가입니다. 단계별로 친절하게 답하세요.")
general_chain = make_chain("당신은 친절한 일반 어시스턴트입니다. 한 문단으로 답하세요.")


# 2. RunnableBranch 구성
#    각 항목: (조건 함수, 해당 체인)
#    마지막 인자: 어떤 조건도 매칭 안 됐을 때의 기본 체인
branch = RunnableBranch(
    (lambda x: any(k in x["question"] for k in ["코드", "파이썬", "함수", "에러"]), code_chain),
    (lambda x: any(k in x["question"] for k in ["요리", "레시피", "맛", "요리법"]),  cooking_chain),
    general_chain,  # default
)


# 3. 라우팅된 경로를 보여주기 위한 디버그 wrapper
from langchain_core.runnables import RunnableLambda

def label_route(question):
    if any(k in question for k in ["코드", "파이썬", "함수", "에러"]):
        return "코딩 체인"
    if any(k in question for k in ["요리", "레시피", "맛", "요리법"]):
        return "요리 체인"
    return "일반 체인"


# 4. 테스트
questions = [
    "파이썬으로 리스트 정렬하는 코드 알려줘",
    "김치찌개 레시피가 뭐야?",
    "오늘 점심 뭐 먹지?",
]

print("=" * 60)
print("RunnableBranch — 입력에 따라 다른 체인으로 자동 라우팅")
print("=" * 60)

for q in questions:
    print(f"\n[질문]    {q}")
    print(f"[라우팅]  {label_route(q)}")
    answer = branch.invoke({"question": q})
    print(f"[답변]    {answer[:120]}{'...' if len(answer) > 120 else ''}")
