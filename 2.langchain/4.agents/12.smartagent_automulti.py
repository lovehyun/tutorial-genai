# 1. 사용자 질문을 받으면
# 2. LLM이 다음 중 하나를 선택:
#  - google-search (실시간 검색용)
#  - wikipedia (백과사전 지식)
#  - llm-math (수학 계산)
#  - human (사람에게 직접 질문)
#  - llm-only (내부 GPT 답변으로 충분)
# 3. 해당 툴만 포함된 Agent를 동적으로 생성하여 실행
# 4. 모든 처리는 JSON 판단에 기반

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain_core.runnables import RunnableLambda
import json
import re

# 1. 환경변수 로드
load_dotenv()

# 2. LLM 설정 (GPT-4o)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# 3. 사용 가능한 툴 이름 정의
tool_names = ["google-search", "wikipedia", "llm-math", "human"]
tool_list = load_tools(tool_names, llm=llm)
tool_map = dict(zip(tool_names, tool_list))  # 안전한 매핑

# 4. 도구 선택 판단 함수 (LLM 이용)
def decide_tool(user_input: str):
    prompt = f"""
You are a tool selection expert for an AI agent.  
Decide which tool (if any) should be used to answer the user's question.

Available tools:
- google-search: For real-time information like news or weather
- wikipedia: For general facts or well-known knowledge
- llm-math: For any mathematical calculations
- human: If human clarification or input is explicitly requested
- llm-only: If the LLM itself can confidently answer without tools

Respond in this JSON format (no explanation):

{{
  "tool_needed": true/false,
  "tool_name": "google-search" | "wikipedia" | "llm-math" | "human" | "llm-only"
}}

User Question: "{user_input}"
"""
    response = llm.invoke(prompt).content
    print("\n[툴 판단 RAW 응답]:", response)
    
    # JSON 팧싱
    try:
        response = re.sub(r"```(json)?", "", response).strip("` \n")
        return json.loads(response)
    except:
        print("[WARN] JSON 파싱 실패, fallback to llm-only")
        return {"tool_needed": False, "tool_name": "llm-only"}

# 5. 라우팅 실행 체인
def smart_router(input):
    user_input = input["input"]
    decision = decide_tool(user_input)
    tool_name = decision.get("tool_name")

    if tool_name == "llm-only":
        print("\n[LLM 직접 응답]")
        response = llm.invoke(user_input)
        return {"output": response.content.strip()}

    elif decision.get("tool_needed") and tool_name in tool_names:
        print(f"\n['{tool_name}' 툴 사용 결정 → Agent 실행]")
        selected_tool = [tool_map[tool_name]]
        agent = initialize_agent(
            tools=selected_tool,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        return agent.invoke({"input": user_input})
    
    else:
        print("\n[툴 이름 불일치 → LLM fallback]")
        response = llm.invoke(user_input)
        return {"output": response.content.strip()}

# 6. 체인 래퍼
smart_chain = RunnableLambda(smart_router)

# 7. 다양한 테스트 입력
inputs = [
    {"input": "2025년 미국 대통령은 누구야?"},              # → google-search
    {"input": "고양이는 왜 야옹거려?"},                      # → wikipedia
    {"input": "153 * (3.2 + 4.8)는 얼마야?"},                # → llm-math
    {"input": "너 말고 사람한테 직접 물어보고 싶어"},         # → human
    {"input": "GPT-4와 GPT-3.5의 차이를 알려줘"},            # → llm-only
]

# 8. 실행
for item in inputs:
    print(f"\n[질문] {item['input']}")
    result = smart_chain.invoke(item)
    print("[응답]", result["output"])
