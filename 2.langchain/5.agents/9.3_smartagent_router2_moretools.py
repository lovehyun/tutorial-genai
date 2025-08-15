# 1. 사용자 질문을 받으면
# 2. LLM이 다음 중 하나를 선택:
#  - google-search (실시간 검색용)
#  - wikipedia (백과사전 지식)
#  - llm-math (수학 계산)
#  - human (사람에게 직접 질문)
#  - llm-only (내부 GPT 답변으로 충분)
# 3. 해당 툴만 포함된 Agent를 동적으로 생성하여 실행
# 4. 모든 처리는 JSON 판단에 기반

# pip install -U langchain langchain_openai langchain_community python-dotenv

from __future__ import annotations
from typing import Literal
import json
import re

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain.chains import LLMMathChain
from langchain.tools import Tool

# -----------------------------
# 0) 환경 변수
# -----------------------------
load_dotenv()

# -----------------------------
# 1) LLM 인스턴스 (비용/성능 최적화 분리)
# -----------------------------
judge_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    timeout=30,
    max_retries=2,
)
answer_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    timeout=60,
    max_retries=2,
)

# -----------------------------
# 2) 도구 준비
# - google-search, wikipedia는 load_tools로
# - llm-math는 LLMMathChain으로 Tool 래핑
# - human은 간단한 CLI 입력으로 샘플 구현
# -----------------------------
# 검색/위키
base_tools = load_tools(["google-search", "wikipedia"], llm=answer_llm, verbose=True)

# 이름 기준 매핑 (안전하게 보장)
tool_map = {t.name: t for t in base_tools}

# 수학 계산 체인 → Tool 래핑
math_chain = LLMMathChain.from_llm(llm=answer_llm, verbose=True)
math_tool = Tool(
    name="llm-math",
    func=math_chain.run,
    description="Use this for math calculations. Input should be a math expression.",
)
tool_map["llm-math"] = math_tool

# human 간단 구현 (CLI)
def ask_human(question: str) -> str:
    print("\n[HUMAN INPUT REQUEST] 에이전트가 사람 의견을 요청합니다.")
    try:
        return input(f"사용자에게 질문: {question}\n사람의 답변 입력: ").strip()
    except EOFError:
        return "No human input available in this environment."

human_tool = Tool(
    name="human",
    func=ask_human,
    description="Ask the human for clarification or additional info via console input.",
)
tool_map["human"] = human_tool

# -----------------------------
# 3) 구조화 판정 스키마
# -----------------------------
class Decision(BaseModel):
    tool_needed: bool = Field(..., description="Whether an external tool should be used.")
    tool_name: Literal["google-search", "wikipedia", "llm-math", "human", "llm-only"] = Field(
        ..., description="Selected tool name or 'llm-only'."
    )
    reason: str = Field(..., description="Short reason for auditing/logging.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the decision.")

decision_parser = judge_llm.with_structured_output(Decision)

# -----------------------------
# 4) 판정 프롬프트 (간결/명확)
# -----------------------------
DECIDE_PROMPT = """You are a tool selection expert for an AI agent.
Choose the best SINGLE option for answering the user's question.

Available tools:
- google-search: Real-time or fast-changing info (news, weather, prices, schedules, current leaders)
- wikipedia: General facts or well-known background knowledge
- llm-math: Arithmetic or equation solving; when exact computation is needed
- human: When human clarification is explicitly requested
- llm-only: When the model can confidently answer without tools

Return a structured JSON object with fields:
- tool_needed: boolean
- tool_name: one of ["google-search","wikipedia","llm-math","human","llm-only"]
- reason: short justification
- confidence: 0.0~1.0

User Question: "{q}"
"""

# -----------------------------
# 5) 하드 규칙 (빠른 우회로)
#    - 비용 절감 & 레이턴시 개선
# -----------------------------
ALWAYS_TOOL_KEYWORDS = {
    "google-search": ("날씨", "오늘", "실시간", "뉴스", "속보", "대통령", "총리", "선거",
                      "환율", "가격", "주가", "스코어", "일정", "시간표", "방송", "티켓"),
    "llm-math": ("계산", "더해", "곱해", "나눠", "제곱", "+", "-", "*", "/", "%"),
    # wikipedia는 과도 매칭 위험이 있어 보통 LLM 판정에 맡기는 편
}

def hard_rule_decision(user_input: str) -> Decision | None:
    text = user_input.strip()
    # google-search 고정
    if any(k in text for k in ALWAYS_TOOL_KEYWORDS["google-search"]):
        return Decision(tool_needed=True, tool_name="google-search",
                        reason="Hard rule: real-time/fast-changing keyword matched", confidence=0.95)
    # llm-math 고정
    if any(k in text for k in ALWAYS_TOOL_KEYWORDS["llm-math"]):
        return Decision(tool_needed=True, tool_name="llm-math",
                        reason="Hard rule: math keyword/operator matched", confidence=0.95)
    return None

# -----------------------------
# 6) 유틸: 출력 정규화
# -----------------------------
def normalize_output(x) -> dict:
    """에이전트/LLM 호출 결과를 항상 {'output': str}로 정규화."""
    if isinstance(x, dict) and "output" in x:
        return {"output": x["output"].strip()}
    if isinstance(x, str):
        return {"output": x.strip()}
    if hasattr(x, "content"):  # ChatOpenAI Message
        return {"output": x.content.strip()}
    return {"output": str(x).strip()}

# -----------------------------
# 7) 라우터
# -----------------------------
def decide_tool(user_input: str) -> Decision:
    # (A) 하드 규칙 먼저
    hr = hard_rule_decision(user_input)
    if hr is not None:
        return hr

    # (B) 구조화 판정
    prompt = DECIDE_PROMPT.format(q=user_input)
    try:
        decision = decision_parser.invoke({"input": prompt})
        return decision
    except Exception as e:
        # 드물게 구조화 실패 시, 가벼운 파서로 복구 시도
        raw = judge_llm.invoke(prompt).content
        # 코드블록 제거
        raw = re.sub(r"```(json)?", "", raw).strip("` \n")
        try:
            data = json.loads(raw)
            return Decision(**data)
        except Exception:
            # 최후의 안전망
            return Decision(tool_needed=False, tool_name="llm-only",
                            reason=f"Fallback due to parse error: {e}", confidence=0.3)

def run_one(user_input: str) -> dict:
    decision = decide_tool(user_input)
    print(f"\n[판정] tool_needed={decision.tool_needed}, tool_name={decision.tool_name}, "
          f"conf={decision.confidence:.2f}, reason={decision.reason}")

    # llm-only → 검색 없이 LLM으로 바로 답변
    if not decision.tool_needed or decision.tool_name == "llm-only":
        resp = answer_llm.invoke(user_input)
        return normalize_output(resp)

    # human → 사람에게 물어보기
    if decision.tool_name == "human":
        # 질문 자체를 그대로 사람에게 전달
        human_answer = human_tool.func(user_input)
        return {"output": f"(사람의 답변) {human_answer}"}

    # 선택된 단일 툴만 포함한 에이전트 동적 생성
    if decision.tool_name in tool_map:
        selected_tool = [tool_map[decision.tool_name]]
        agent = initialize_agent(
            tools=selected_tool,
            llm=answer_llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            verbose=True,
        )
        result = agent.invoke({"input": user_input})
        return normalize_output(result)

    # 매핑 실패 시 최종 안전망
    resp = answer_llm.invoke(user_input)
    return normalize_output(resp)

smart_chain = RunnableLambda(lambda x: run_one(x["input"]))

# -----------------------------
# 8) 테스트
# -----------------------------
if __name__ == "__main__":
    tests = [
        {"input": "2025년 미국 대통령은 누구야?"},                 # google-search
        {"input": "153 * (3.2 + 4.8)는 얼마야?"},                 # llm-math
        {"input": "너 말고 사람한테 직접 물어보고 싶어"},           # human
        {"input": "고양이는 왜 야옹거려?"},                        # wikipedia or llm-only (판정에 따라)
        {"input": "GPT-4와 GPT-3.5의 차이를 알려줘"},              # llm-only 가능
    ]
    for t in tests:
        print(f"\n[질문] {t['input']}")
        out = smart_chain.invoke(t)
        print("[응답]", out["output"])
