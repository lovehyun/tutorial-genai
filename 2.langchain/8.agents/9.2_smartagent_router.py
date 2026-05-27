from dotenv import load_dotenv
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

load_dotenv()

# 1) LLM 분리: 판정은 가볍게, 본답변은 고품질
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=2)
answer_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, timeout=60, max_retries=2)

# 2) Tool/Agent
tools = load_tools(["google-search"])
agent = initialize_agent(
    tools=tools,
    llm=answer_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
)

# 3) 구조화 출력 스키마 (툴 사용 여부 + 간단한 이유)
class JudgeSchema(BaseModel):
    use_tool: bool
    reason: str

judge = judge_llm.with_structured_output(JudgeSchema)

# 3-1) 프롬프트 체인 (dict 입력 지원)
judge_prompt = PromptTemplate.from_template(
    "You are a tool selection judge. Return JSON with fields: use_tool(boolean), reason(string).\n"
    "Question: \"{question}\""
)
judge_chain = judge_prompt | judge

# 4) 하드 규칙(빠른 필터) + LLM 판정
ALWAYS_TOOL_KEYWORDS = ("날씨", "오늘", "실시간", "뉴스", "속보", "환율", "가격", "대통령", "총리", "선거", "주가", "스코어")

def normalize_output(x):
    # agent.invoke가 dict 또는 str을 반환할 수 있으니 정규화
    if isinstance(x, dict) and "output" in x:
        return {"output": x["output"].strip()}
    if isinstance(x, str):
        return {"output": x.strip()}
    # ChatOpenAI.invoke 응답 처리
    if hasattr(x, "content"):
        return {"output": x.content.strip()}
    
    return {"output": str(x).strip()}

def smart_router(inp):
    user_input = inp["input"]

    # (A) 하드 규칙: 특정 키워드면 바로 툴 사용
    if any(k in user_input for k in ALWAYS_TOOL_KEYWORDS):
        print("\n[판단: 하드 규칙 매치 => 툴 사용]")
        return normalize_output(agent.invoke({"input": user_input}))

    # (B) LLM 구조화 판정 (dict 입력 가능)
    j = judge_chain.invoke({"question": user_input})
    print(f"\n[판단: use_tool={j.use_tool} | reason={j.reason}]")

    if j.use_tool:
        return normalize_output(agent.invoke({"input": user_input}))
    else:
        # 툴 없이 바로 답변
        resp = answer_llm.invoke(user_input)  # 문자열 입력 보장
        return normalize_output(resp)

smart_chain = RunnableLambda(smart_router)

# 테스트
inputs = [
    {"input": "서울의 오늘 날씨는 어때?"},
    {"input": "GPT-4o 모델은 어떤 기능을 가지고 있어?"},
    {"input": "2025년 미국 대통령은 누구야?"},
    {"input": "고양이는 왜 귀엽다고 느껴질까?"}
]

for item in inputs:
    print(f"\n[질문] {item['input']}")
    try:
        result = smart_chain.invoke(item)
        print("[응답]", result["output"])
    except Exception as e:
        print(f"[오류 발생] {e}")
