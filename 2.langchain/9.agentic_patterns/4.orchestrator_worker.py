"""
4_orchestrator_worker.py - Orchestrator-Worker 패턴

이 파일은 Anthropic의 Agentic 디자인 패턴 중 'Orchestrator-Worker'를 구현합니다.
오케스트레이터 LLM이 작업을 동적으로 분해하고, 각 하위 작업을 워커에게 위임한 후,
결과를 종합하여 최종 출력을 생성합니다. LangGraph로 상태 관리를 합니다.

예제: "Python 웹 크롤러" 코드 리뷰 요청 → 동적 분해 → 워커별 리뷰 → 종합
"""

import json
from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

print("=" * 60)
print("Agentic 패턴 4: Orchestrator-Worker (동적 작업 분해·위임·종합)")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# 1. 상태 정의
# ============================================================
class OrchestratorState(TypedDict):
    request: str           # 원본 요청
    subtasks: List[str]    # 분해된 하위 작업 목록
    results: List[str]     # 각 워커의 결과
    final_output: str      # 종합 최종 출력


# ============================================================
# 2. 오케스트레이터 노드 — 작업 분해
# ============================================================
def orchestrator(state: OrchestratorState) -> dict:
    """요청을 분석하고 하위 작업으로 동적 분해합니다."""
    print("\n[오케스트레이터] 작업 분해 중...")

    response = llm.invoke([
        SystemMessage(content="""당신은 작업 분해 전문가입니다.
사용자의 요청을 분석하여 2~4개의 독립적인 하위 작업으로 분해해주세요.
반드시 JSON 배열 형식으로만 답하세요. 예: ["작업1", "작업2", "작업3"]"""),
        HumanMessage(content=f"요청: {state['request']}")
    ])

    try:
        subtasks = json.loads(response.content)
    except json.JSONDecodeError:
        subtasks = [state["request"]]

    print(f"  분해된 작업 ({len(subtasks)}개):")
    for i, task in enumerate(subtasks, 1):
        print(f"    {i}. {task}")

    return {"subtasks": subtasks, "results": []}


# ============================================================
# 3. 워커 노드 — 하위 작업 실행
# ============================================================
def worker(state: OrchestratorState) -> dict:
    """각 하위 작업을 순차적으로 실행합니다."""
    print("\n[워커] 하위 작업 실행 중...")
    results = []

    for i, subtask in enumerate(state["subtasks"], 1):
        print(f"  워커 {i}/{len(state['subtasks'])}: {subtask[:50]}...")
        response = llm.invoke([
            SystemMessage(content="주어진 작업을 수행하고 결과를 간결하게 보고해주세요."),
            HumanMessage(content=subtask)
        ])
        results.append(f"[작업 {i}] {subtask}\n결과: {response.content}")

    return {"results": results}


# ============================================================
# 4. 종합 노드 — 결과 통합
# ============================================================
def synthesizer(state: OrchestratorState) -> dict:
    """모든 워커 결과를 종합하여 최종 출력을 생성합니다."""
    print("\n[종합] 결과 통합 중...")

    all_results = "\n\n".join(state["results"])
    response = llm.invoke([
        SystemMessage(content="다음 하위 작업들의 결과를 종합하여 하나의 완성된 보고서로 통합해주세요."),
        HumanMessage(content=f"원본 요청: {state['request']}\n\n하위 작업 결과:\n{all_results}")
    ])

    return {"final_output": response.content}


# ============================================================
# 5. LangGraph 워크플로우 구성
# ============================================================
graph = StateGraph(OrchestratorState)

graph.add_node("orchestrator", orchestrator)
graph.add_node("worker", worker)
graph.add_node("synthesizer", synthesizer)

# 흐름: 오케스트레이터 → 워커 → 종합
graph.add_edge(START, "orchestrator")
graph.add_edge("orchestrator", "worker")
graph.add_edge("worker", "synthesizer")
graph.add_edge("synthesizer", END)

app = graph.compile()
print("Orchestrator-Worker 그래프 컴파일 완료")
print("실행 흐름: START → orchestrator → worker → synthesizer → END")

# ============================================================
# 실행
# ============================================================
request = "Python으로 작성된 간단한 웹 크롤러 코드를 리뷰해주세요. 보안, 성능, 코드 품질 관점에서 분석이 필요합니다."

print(f"\n요청: {request}")
result = app.invoke({
    "request": request,
    "subtasks": [],
    "results": [],
    "final_output": "",
})

print("\n" + "=" * 60)
print("최종 출력:")
print("=" * 60)
print(result["final_output"])

print("\n" + "=" * 60)
print("설명:")
print("1. Orchestrator-Worker 패턴은 오케스트레이터가 작업을 동적으로 분해합니다.")
print("2. 분해된 작업 수와 내용은 입력에 따라 달라집니다 (Parallelization과의 차이).")
print("3. 워커가 각 하위 작업을 독립적으로 수행하고, 종합 노드가 결과를 통합합니다.")
print("4. LangGraph의 StateGraph로 상태를 관리하여 단계 간 데이터를 자연스럽게 전달합니다.")
print("\n적합한 사용 사례: 코드 리뷰, 복잡한 분석, 멀티 에이전트 협업, 동적 작업 분배")
