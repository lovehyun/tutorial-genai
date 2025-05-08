from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain_core.runnables import RunnableLambda

load_dotenv()

# LLM (gpt-4o 사용)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# Google Search 도구 로드
tools = load_tools(["google-search"])

# Agent 정의
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 도구 사용 여부를 LLM에게 판단하게 하는 체인
def smart_router(input):
    user_input = input["input"]

    # 1. LLM에게 이 질문에 툴이 필요한지 판단 요청
    judge_prompt = f"""
You are an AI assistant that determines whether a user's question requires using an external tool like Google Search to answer.
Answer only "Yes" or "No".

Question: "{user_input}"
Is external tool usage required?
"""
    judge_response = llm.invoke(judge_prompt).content.strip().lower()

    # 2. 판단 결과에 따라 분기
    if "yes" in judge_response:
        print("\n[판단 결과: 툴 필요 → 에이전트 호출]")
        return agent.invoke({"input": user_input})
    else:
        print("\n[판단 결과: 툴 불필요 → LLM 직접 응답]")
        response = llm.invoke(user_input)
        return {"output": response.content.strip()}

# 체인 래퍼
smart_chain = RunnableLambda(smart_router)

# 테스트
inputs = [
    {"input": "서울의 오늘 날씨는 어때?"},
    {"input": "GPT-4o 모델은 어떤 기능을 가지고 있어?"},
    {"input": "2025년 대선 후보는 누구야?"},
    {"input": "고양이는 왜 귀엽다고 느껴질까?"}
]

for item in inputs:
    print(f"\n[질문] {item['input']}")
    result = smart_chain.invoke(item)
    print("[응답]", result["output"])
