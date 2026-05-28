"""
[Task] 고객센터 라우터

고객 질문의 키워드로 담당 상담원 페르소나 체인을 자동 선택합니다.
RunnableBranch 의 실전 활용 예시.

  결제 관련 → 결제 상담원
  배송 관련 → 배송 상담원
  오류 관련 → 기술 지원
  그 외     → 일반 상담원 (default)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

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


payment_chain  = make_chain("당신은 결제 상담원입니다. 결제·환불·청구 문제를 친절히 안내하세요.")
delivery_chain = make_chain("당신은 배송 상담원입니다. 배송 조회·지연·반품을 안내하세요.")
tech_chain     = make_chain("당신은 기술 지원 담당자입니다. 앱/서비스 오류를 단계별로 해결해주세요.")
general_chain  = make_chain("당신은 일반 고객 상담원입니다. 친절하고 간결하게 답하세요.")

branch = RunnableBranch(
    (lambda x: any(k in x["question"] for k in ["결제", "환불", "청구"]),  payment_chain),
    (lambda x: any(k in x["question"] for k in ["배송", "택배", "반품"]),  delivery_chain),
    (lambda x: any(k in x["question"] for k in ["오류", "에러", "안돼요"]), tech_chain),
    general_chain,  # default
)

questions = [
    "배송이 아직 안왔어요. 언제쯤 도착할까요?",
    "결제가 두 번 됐는데 환불 가능할까요?",
    "앱 로그인이 안돼요. 오류 메시지가 떠요.",
    "이용 시간은 어떻게 되나요?",
]

for q in questions:
    print("=" * 60)
    print(f"[고객] {q}")
    print(f"[상담원] {branch.invoke({'question': q})}")
