"""
6_self_correction_loop.py - Self-Correction Loop (자기 수정 루프)

이 파일은 LangGraph로 Self-Correction Loop를 구현하는 방법을 보여줍니다.
LLM이 코드를 생성하고, 검증 단계에서 문제를 발견하면 피드백과 함께
재생성을 요청하는 순환 루프를 구현합니다.

흐름: 코드 생성 → 코드 검증 → (실패 시) 피드백 → 재생성 → ... → 최종 출력
"""

from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

print("=" * 60)
print("Self-Correction Loop: 코드 생성 → 검증 → 피드백 → 재생성")
print("=" * 60)

# LLM 초기화
generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
validator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# 1. 상태 정의
# ============================================================
class SelfCorrectionState(TypedDict):
    task: str                  # 코드 생성 요청
    code: str                  # 현재 생성된 코드
    validation_result: str     # 검증 결과 (PASS/FAIL)
    feedback: str              # 검증 피드백
    iteration: int             # 반복 횟수
    history: List[str]         # 이전 코드 버전 기록


# ============================================================
# 2. 코드 생성 노드
# ============================================================
def generate_code(state: SelfCorrectionState) -> dict:
    """코드를 생성하거나 피드백을 반영하여 수정합니다."""
    iteration = state["iteration"] + 1
    print(f"\n[생성] 반복 {iteration}회차...")

    if state["feedback"]:
        # 피드백 기반 수정
        prompt = f"""다음 코드에 문제가 발견되었습니다. 피드백을 반영하여 수정해주세요.

요청: {state['task']}

현재 코드:
{state['code']}

피드백:
{state['feedback']}

수정된 코드만 출력해주세요 (설명 없이 코드만):"""
    else:
        # 초기 생성
        prompt = f"""다음 요청에 맞는 Python 코드를 작성해주세요.
설명 없이 코드만 출력해주세요.

요청: {state['task']}"""

    response = generator_llm.invoke([HumanMessage(content=prompt)])
    code = response.content
    history = state["history"] + [code]

    print(f"  코드 생성 완료 ({len(code)}자)")
    return {"code": code, "iteration": iteration, "history": history}


# ============================================================
# 3. 코드 검증 노드
# ============================================================
def validate_code(state: SelfCorrectionState) -> dict:
    """생성된 코드의 품질을 검증합니다."""
    print(f"\n[검증] 코드 검증 중 (반복 {state['iteration']}회차)...")

    response = validator_llm.invoke([
        SystemMessage(content="""당신은 Python 코드 리뷰 전문가입니다.
다음 기준으로 코드를 검증하세요:

1. 구문 오류가 없는가?
2. 함수/변수 네이밍이 적절한가?
3. 엣지 케이스 처리가 되어 있는가?
4. 타입 힌트가 포함되어 있는가?

반드시 다음 형식으로 답하세요:
결과: PASS 또는 FAIL
피드백: 구체적인 개선 사항 (PASS여도 간단한 코멘트)"""),
        HumanMessage(content=f"요청: {state['task']}\n\n코드:\n{state['code']}")
    ])

    result = response.content

    # 결과 파싱
    validation = "FAIL"
    feedback = result
    for line in result.split("\n"):
        if "결과" in line:
            validation = "PASS" if "PASS" in line.upper() else "FAIL"
        if "피드백" in line:
            feedback = line.split(":", 1)[-1].strip()

    print(f"  검증 결과: {validation}")
    print(f"  피드백: {feedback[:100]}...")

    return {"validation_result": validation, "feedback": feedback}


# ============================================================
# 4. 조건부 라우팅 — 계속 수정할지 종료할지 결정
# ============================================================
def should_retry(state: SelfCorrectionState) -> str:
    """검증 통과 여부 및 최대 반복 횟수를 확인합니다."""
    if state["validation_result"] == "PASS":
        print(f"\n[라우터] 검증 통과 → 완료!")
        return "end"
    if state["iteration"] >= 3:
        print(f"\n[라우터] 최대 반복(3회) 도달 → 현재 버전으로 종료")
        return "end"
    print(f"\n[라우터] 검증 실패 → 재생성")
    return "retry"


# ============================================================
# 5. LangGraph 순환 그래프 구성
# ============================================================
graph = StateGraph(SelfCorrectionState)

graph.add_node("generate", generate_code)
graph.add_node("validate", validate_code)

graph.add_edge(START, "generate")
graph.add_edge("generate", "validate")
graph.add_conditional_edges(
    "validate",
    should_retry,
    {"retry": "generate", "end": END},
)

app = graph.compile()
print("Self-Correction 그래프 컴파일 완료")
print("실행 흐름: START → generate ⇄ validate → END")

# ============================================================
# 실행
# ============================================================
task = "두 개의 정렬된 리스트를 병합하여 하나의 정렬된 리스트로 반환하는 함수를 작성하세요. 타입 힌트를 포함하고, 빈 리스트 입력도 처리해야 합니다."

print(f"\n작업: {task}")
result = app.invoke({
    "task": task,
    "code": "",
    "validation_result": "",
    "feedback": "",
    "iteration": 0,
    "history": [],
})

print("\n" + "=" * 60)
print(f"최종 코드 (반복 {result['iteration']}회, 결과: {result['validation_result']}):")
print("=" * 60)
print(result["code"])

if len(result["history"]) > 1:
    print(f"\n수정 이력 ({len(result['history'])}버전):")
    for i, version in enumerate(result["history"], 1):
        first_line = version.strip().split("\n")[0]
        print(f"  v{i}: {first_line[:80]}...")

print("\n" + "=" * 60)
print("설명:")
print("1. Self-Correction Loop는 LLM 출력을 자동으로 검증하고 개선하는 패턴입니다.")
print("2. 생성 노드와 검증 노드 사이의 순환으로 반복적 개선이 이루어집니다.")
print("3. 검증 통과(PASS) 또는 최대 반복 횟수 도달 시 루프를 종료합니다.")
print("4. 검증 단계에서 실제 코드 실행(exec/subprocess)을 추가하면 더 강력한 검증이 가능합니다.")
