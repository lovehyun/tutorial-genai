# pip install -U langchain langchain_openai langchain_community google-api-python-client python-dotenv

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain_core.runnables import RunnableLambda

# 효율성: 모든 질문에 검색을 돌리면 느리고 API 비용이 커집니다.
# 정확성: 최신 정보·날씨·가격 등 실시간/외부 데이터가 필요한 경우만 검색 툴을 호출하고, 나머지는 모델 자체 지식으로 답하도록 분기합니다.
# 유연성: 조건(키워드 리스트)을 바꿔서 "검색 필요 여부" 를 쉽게 조정할 수 있습니다.

# 1. 환경변수 로드
load_dotenv()

# 2. LLM (ChatOpenAI, gpt-4o)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# 3. 툴 로드 (GOOGLE_API_KEY와 GOOGLE_CSE_ID가 .env에 있어야 함)
tools = load_tools(["google-search"])

# 4. Agent 정의 (ZeroShot + ReAct)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 5. 스마트 라우터 체인 정의
def smart_router(input):
    user_input = input["input"]
    keywords = ["날씨", "검색", "오늘", "실시간", "뉴스", "정보", "가격", "환율"]
    if any(k in user_input for k in keywords):
        print("\n[도구 사용: 에이전트 호출 중...]")
        return agent.invoke(input)
    else:
        print("\n[도구 없이: LLM 직접 응답 중...]")
        response = llm.invoke(user_input)
        return {"output": response.content.strip()}

# 6. 체인 래퍼 구성
smart_chain = RunnableLambda(smart_router)

# 7. 테스트 실행
inputs = [
    {"input": "서울의 오늘 날씨는 어때?"},
    {"input": "GPT-4o 모델은 어떤 특징이 있어?"},
    {"input": "2025년 미국 대통령은 누구야?"},
    {"input": "AI는 우리 삶에 어떤 영향을 줄까?"}
]

for item in inputs:
    print(f"\n[질문] {item['input']}")
    result = smart_chain.invoke(item)
    print("[응답]", result["output"])
