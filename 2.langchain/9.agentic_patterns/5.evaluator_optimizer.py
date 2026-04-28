"""
5_evaluator_optimizer.py - Evaluator-Optimizer 패턴

이 파일은 Anthropic의 Agentic 디자인 패턴 중 'Evaluator-Optimizer'를 구현합니다.
생성자(Generator)가 출력을 만들고, 평가자(Evaluator)가 품질을 평가하여
기준을 충족할 때까지 반복적으로 개선합니다. LangGraph의 순환 그래프로 구현합니다.

예제: 마케팅 카피 생성 → 평가 → 피드백 기반 개선 → 재평가 (최대 3회)
"""

from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

print("=" * 60)
print("Agentic 패턴 5: Evaluator-Optimizer (생성→평가→개선 루프)")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# 1. 상태 정의
# ============================================================
class EvalOptState(TypedDict):
    task: str                  # 원본 작업
    current_output: str        # 현재 생성물
    feedback: str              # 평가자 피드백
    score: int                 # 평가 점수 (1~10)
    iteration: int             # 현재 반복 횟수
    history: List[str]         # 이전 생성물 기록


# ============================================================
# 2. 생성자 노드 — 초기 생성 또는 피드백 기반 개선
# ============================================================
def generator(state: EvalOptState) -> dict:
    """작업에 대한 출력을 생성하거나 피드백을 반영하여 개선합니다."""
    iteration = state["iteration"] + 1
    print(f"\n[생성자] 반복 {iteration}회차...")

    if state["feedback"]:
        # 피드백이 있으면 개선
        prompt = f"""이전 결과를 다음 피드백을 반영하여 개선해주세요.

작업: {state['task']}

이전 결과:
{state['current_output']}

피드백:
{state['feedback']}

개선된 결과:"""
    else:
        # 초기 생성
        prompt = f"""다음 작업을 수행해주세요.

작업: {state['task']}

결과:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    output = response.content
    history = state["history"] + [output]

    print(f"  생성 완료 (길이: {len(output)}자)")
    return {"current_output": output, "iteration": iteration, "history": history}


# ============================================================
# 3. 평가자 노드 — 품질 평가 및 피드백
# ============================================================
def evaluator(state: EvalOptState) -> dict:
    """생성물의 품질을 평가하고 개선 피드백을 제공합니다."""
    print(f"\n[평가자] 평가 중 (반복 {state['iteration']}회차)...")

    response = evaluator_llm.invoke([
        SystemMessage(content="""당신은 마케팅 카피 품질 평가 전문가입니다.
다음 기준으로 평가하고 점수(1~10)와 피드백을 제공해주세요.

평가 기준:
1. 주목성: 눈길을 끄는가?
2. 명확성: 메시지가 분명한가?
3. 설득력: 행동을 유도하는가?
4. 간결성: 불필요한 내용이 없는가?

반드시 다음 형식으로 답하세요:
점수: [1~10 숫자]
피드백: [구체적인 개선 사항]"""),
        HumanMessage(content=f"작업: {state['task']}\n\n평가 대상:\n{state['current_output']}")
    ])

    result = response.content

    # 점수 파싱
    score = 5  # 기본값
    for line in result.split("\n"):
        if "점수" in line:
            digits = "".join(c for c in line if c.isdigit())
            if digits:
                score = min(10, max(1, int(digits[:2])))
                break

    # 피드백 파싱
    feedback = result
    for line in result.split("\n"):
        if "피드백" in line:
            feedback = line.split(":", 1)[-1].strip()
            break

    print(f"  점수: {score}/10")
    print(f"  피드백: {feedback[:100]}...")

    return {"score": score, "feedback": feedback}


# ============================================================
# 4. 조건부 라우팅 — 계속 개선할지 종료할지 결정
# ============================================================
def should_continue(state: EvalOptState) -> str:
    """점수가 기준 이상이거나 최대 반복 횟수에 도달하면 종료합니다."""
    if state["score"] >= 8:
        print(f"\n[라우터] 점수 {state['score']}/10 >= 8 → 완료!")
        return "end"
    if state["iteration"] >= 3:
        print(f"\n[라우터] 최대 반복 횟수(3) 도달 → 종료")
        return "end"
    print(f"\n[라우터] 점수 {state['score']}/10 < 8 → 재생성")
    return "continue"


# ============================================================
# 5. LangGraph 순환 그래프 구성
# ============================================================
graph = StateGraph(EvalOptState)

graph.add_node("generator", generator)
graph.add_node("evaluator", evaluator)

graph.add_edge(START, "generator")
graph.add_edge("generator", "evaluator")
graph.add_conditional_edges(
    "evaluator",
    should_continue,
    {"continue": "generator", "end": END},
)

app = graph.compile()
print("Evaluator-Optimizer 그래프 컴파일 완료")
print("실행 흐름: START → generator ⇄ evaluator → END (순환)")

# ============================================================
# 실행
# ============================================================
task = "AI 코딩 교육 플랫폼의 30자 이내 마케팅 슬로건을 작성해주세요. 대상: 프로그래밍 입문자."

print(f"\n작업: {task}")
result = app.invoke({
    "task": task,
    "current_output": "",
    "feedback": "",
    "score": 0,
    "iteration": 0,
    "history": [],
})

print("\n" + "=" * 60)
print(f"최종 결과 (반복 {result['iteration']}회, 점수 {result['score']}/10):")
print("=" * 60)
print(result["current_output"])

if len(result["history"]) > 1:
    print(f"\n개선 과정 ({len(result['history'])}단계):")
    for i, version in enumerate(result["history"], 1):
        print(f"  v{i}: {version[:80]}...")

print("\n" + "=" * 60)
print("설명:")
print("1. Evaluator-Optimizer는 생성과 평가를 반복하여 품질을 점진적으로 개선합니다.")
print("2. LangGraph의 conditional_edges로 순환 그래프를 구현합니다.")
print("3. 평가 점수가 기준(8점) 이상이거나 최대 반복(3회)에 도달하면 종료합니다.")
print("4. 평가자는 낮은 temperature로 일관된 평가를, 생성자는 높은 temperature로 창의적 생성을 합니다.")
print("\n적합한 사용 사례: 콘텐츠 생성, 코드 최적화, 번역 품질 향상, 자동 에세이 개선")
