"""
미들웨어 (2) — PIIMiddleware 로 민감정보(가드레일) 처리.
이 예제: 입력에서 이메일·신용카드 등을 자동 탐지해 마스킹/치환한다.

strategy:
  - redact : [REDACTED_EMAIL] 처럼 통째로 치환
  - mask   : 일부만 가림 (4111********1111)
  - block  : 발견 시 PIIDetectionError 로 차단
  - hash   : 해시값으로 치환
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    llm,
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)

q = "내 이메일은 alice@example.com 이고 카드번호는 4111 1111 1111 1111 이야. 잘 받았는지 확인해줘."
print(f"원본 입력:\n  {q}\n")

result = agent.invoke({"messages": [("user", q)]})

# 미들웨어가 input 메시지를 마스킹한 뒤 모델에 전달 → 첫 human 메시지 확인
print("미들웨어 처리 후(모델이 실제로 본) 입력:")
print(f"  {result['messages'][0].content}\n")
print(f"답변: {result['messages'][-1].content}")


# 정리:
#   - PIIMiddleware(pii_type, strategy=, apply_to_input/output/tool_results=)
#   - 내장 타입: email / credit_card / ip / mac_address / url (+ 커스텀 detector 함수)
#   - strategy='block' 은 발견 시 PIIDetectionError → try/except 로 거부 응답 구성
#   - 출력/도구결과 검사: apply_to_output=True / apply_to_tool_results=True
