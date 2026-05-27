# LLM 6일차: Agent의 이해 (도구 사용 & LangGraph 기초)

## 학습 목표
- LLM이 **툴(도구)**을 선택/호출하여 복합 작업을 수행하는 **에이전트** 개념을 이해합니다.
- ReAct 스타일 추론/행동, LangChain의 AgentExecutor를 이용해 실습합니다.
- LangGraph로 **상태 머신** 기반 워크플로를 구성하는 기초를 익힙니다.

---

## 설치
```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv
```

## 기본 아이디어
1) 사용자 질의 → 모델이 툴 필요성 판단 → 툴 호출 파라미터 생성  
2) 애플리케이션이 실제 함수를 실행 → 결과를 모델에 재주입  
3) 반복하여 최종 답을 생성

---

## 도구 정의(계산기, 검색 흉내, RAG 조회)
```python
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

# 1) 계산기
@tool
def calculator(expression: str) -> str:
    """사칙연산 수식을 계산합니다. 예: '12 * (3 + 2)'."""
    try:
        return str(eval(expression, {"__builtins__":{}}))
    except Exception as e:
        return f"error: {e}"

# 2) 가짜 검색(데모): 실제 서비스에서는 전용 API 사용
@tool
def faux_search(query: str) -> str:
    """간단한 키워드 도움말을 반환(데모)."""
    db = {
        "langchain": "LCEL, Runnables, 체인, 메모리, 에이전트 등",
        "rag": "문서 로딩→청킹→임베딩→검색→생성 파이프라인"
    }
    return db.get(query.lower(), "검색 결과 없음")

tools = [calculator, faux_search]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 도구를 적절히 사용해 정확히 답하는 조력자입니다."),
    ("human", "{input}"),
    ("assistant", "생각: 문제를 해결하기 위해 필요한 도구가 있는지 점검한다.")
])

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

print(executor.invoke({"input":"(12+8)/5 계산해줘"}))
print(executor.invoke({"input":"rag 핵심 단계를 알려줘"}))
```

---

## RAG 도구 연동(선택)
이미 Day 4/5에서 만든 **retriever**를 도구로 노출하면, 에이전트가 필요 시 검색하도록 만들 수 있습니다.

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = Chroma(collection_name="service-docs", persist_directory="chroma_db", embedding_function=emb)
retriever = vs.as_retriever(search_kwargs={"k":4})

@tool
def rag_search(query: str) -> str:
    """업로드된 문서에서 관련 청크를 찾아 요약합니다."""
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join(d.page_content for d in docs) or "관련 문서 없음"
```

`tools = [calculator, faux_search, rag_search]`로 확장 후 `create_react_agent`에 전달하세요.

---

## LangGraph 기초 (상태 머신형 워크플로)
복잡한 에이전트는 명시적 **그래프**로 표현하면 추적/제어가 쉬워집니다.

```python
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

class State(TypedDict):
    question: str
    plan: Optional[str]
    result: Optional[str]

def plan_node(state: State):
    # 간략 플래너: 질문을 요약해 계획 문자열 생성
    state["plan"] = f"질문 분석 후 한 단계 답변: {state['question']}" 
    return state

def answer_node(state: State):
    # 실제로는 LLM 호출/툴 사용이 들어감
    state["result"] = f"플랜에 따라 답변: {state['plan']}"
    return state

graph = StateGraph(State)
graph.add_node("plan", plan_node)
graph.add_node("answer", answer_node)
graph.set_entry_point("plan")
graph.add_edge("plan", "answer")
graph.add_edge("answer", END)
app = graph.compile()

out = app.invoke({"question":"벡터DB가 뭐예요?"})
print(out["result"])
```

---

## 프롬프트 설계 팁(에이전트 전용)
- 역할/목표/제약/툴 리스트/반환 형식 명시
- **헛걸음 방지**: 동일 툴 반복 호출 제한, 최대 스텝 수
- 실패 시 **반성 루프**(self-reflection) 한 번 정도 허용

---

## 실습 과제
1) `rag_search` 도구를 추가하고 “문서 기반 질의”가 들어오면 우선 사용하도록 유도하는 지시를 Prompt에 넣어보세요.  
2) LangGraph 예제에서 plan → tool_call → answer의 3단계로 확장.  
3) **계산기** 도구 악성 입력 방어(안전 eval) 보강.
