# LangGraph 에이전트

> 선형 체인을 넘어 순환(Cycle)과 조건 분기가 가능한 그래프 기반 에이전트를 설계합니다 — StateGraph, 체크포인팅, ReAct 패턴, 멀티 에이전트 아키텍처까지, LangGraph 0.2+로 구현하는 자율형 AI 에이전트의 모든 것

---

## 1. 왜 체인이 아닌 그래프인가

### LangChain LCEL의 한계

LangChain의 LCEL(LangChain Expression Language)은 파이프(`|`) 연산자로 컴포넌트를 연결하여 직관적인 체인을 만들 수 있습니다. 그러나 실무에서 에이전트를 구축하다 보면 LCEL의 선형 구조가 벽이 되는 순간이 옵니다.

```python
# lcel_example.py -- LCEL의 선형 파이프라인 예시
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("다음 질문에 답하세요: {question}")
llm = ChatOpenAI(model="gpt-4o")
parser = StrOutputParser()

# 선형 흐름: prompt → llm → parser (항상 이 순서)
chain = prompt | llm | parser
result = chain.invoke({"question": "파이썬이란?"})
```

위 코드는 깔끔하지만 다음과 같은 상황에서는 대응하기 어렵습니다.

| 상황 | LCEL의 한계 |
|------|-------------|
| LLM이 도구를 호출한 뒤 결과를 다시 LLM에 전달해야 할 때 | 순환(Cycle)이 불가능 |
| 사용자 확인이 필요한 단계에서 멈추고 재개해야 할 때 | 중단/재개 메커니즘 없음 |
| 이전 대화 맥락을 유지하면서 여러 턴을 처리해야 할 때 | 상태 영속성 없음 |
| 조건에 따라 완전히 다른 경로를 타야 할 때 | 복잡한 분기 처리 어려움 |
| 여러 에이전트가 협력해야 할 때 | 멀티 에이전트 구조 어려움 |

### 그래프가 제공하는 해결책

**그래프(Graph)** 구조는 이러한 한계를 근본적으로 해결합니다. 노드(Node)는 실행 단위이고, 엣지(Edge)는 실행 흐름을 정의하며, 조건부 엣지(Conditional Edge)는 런타임에 경로를 결정합니다. 무엇보다 **순환(Cycle)** 이 가능하므로 LLM이 도구를 호출하고, 결과를 받아 다시 판단하는 반복 루프를 자연스럽게 표현할 수 있습니다.

| 특성 | LCEL 체인 | LangGraph |
|------|-----------|-----------|
| 실행 흐름 | 선형, 고정 | 그래프, 동적 |
| 순환(Cycle) | 불가능 | 가능 |
| 조건 분기 | 제한적 | 조건부 엣지 |
| 상태 관리 | 없음 | TypedDict 기반 상태 |
| 영속성 | 없음 | 체크포인팅 |
| 중단/재개 | 불가능 | interrupt_before/after |
| 멀티 에이전트 | 어려움 | 네이티브 지원 |

### LangGraph 소개

**LangGraph**는 LangChain 팀이 개발한 에이전트 오케스트레이션 프레임워크입니다. 핵심 아이디어는 **상태 머신(State Machine)** 을 그래프로 표현하는 것입니다. langgraph 0.2+ 버전부터 API가 안정화되었으며, `langsmith`와 통합하여 에이전트의 실행 과정을 추적하고 디버깅할 수 있습니다.

```bash
# 설치
pip install langgraph langchain-openai langsmith
```

### Chain vs Graph 비교

```mermaid
flowchart LR
    subgraph Chain["LCEL Chain (선형)"]
        direction LR
        C1["Prompt"] --> C2["LLM"] --> C3["Parser"] --> C4["결과"]
    end

    subgraph Graph["LangGraph (그래프)"]
        direction LR
        G1["START"] --> G2["LLM"]
        G2 -->|"도구 필요"| G3["Tool"]
        G3 --> G2
        G2 -->|"최종 응답"| G4["END"]
        G2 -->|"확인 필요"| G5["Human"]
        G5 --> G2
    end

    style C1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style C2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style C3 fill:#0984e3,stroke:#74b9ff,color:#fff
    style C4 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G1 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style G2 fill:#00b894,stroke:#55efc4,color:#fff
    style G3 fill:#e17055,stroke:#fab1a0,color:#fff
    style G4 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style G5 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Chain fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Graph fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

> **핵심 포인트:** LCEL은 단순하고 예측 가능한 파이프라인에 적합하지만, 실제 에이전트는 "판단 → 행동 → 관찰 → 재판단"의 순환 구조가 필요합니다. LangGraph는 이 순환을 일급 시민으로 지원합니다.

---

## 2. StateGraph 기초

### TypedDict로 상태 정의

LangGraph의 핵심은 **상태(State)** 입니다. 그래프의 모든 노드는 상태를 읽고 수정하며, 상태는 `TypedDict`로 타입을 명시합니다. 이는 런타임에 어떤 데이터가 흐르는지 명확하게 보여줍니다.

```python
# state_definition.py -- TypedDict 기반 상태 정의
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """에이전트의 상태를 정의합니다."""
    # 대화 메시지 목록 (리듀서: add_messages)
    messages: Annotated[list[BaseMessage], add_messages]
    # 현재 사용자의 의도
    intent: str
    # 검색 결과
    search_results: list[str]
    # 반복 횟수
    iteration_count: int
```

### add_messages 리듀서

`Annotated[list[BaseMessage], add_messages]`에서 `add_messages`는 **리듀서(Reducer)** 입니다. 노드가 메시지 목록을 반환하면, 기존 목록을 덮어쓰는 것이 아니라 **기존 메시지에 추가(append)** 합니다. 같은 ID의 메시지가 이미 있으면 업데이트합니다.

```python
# reducer_example.py -- add_messages 리듀서의 동작 방식
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

existing = [HumanMessage(content="안녕하세요")]
new = [AIMessage(content="반갑습니다!")]
result = add_messages(existing, new)
# result: [HumanMessage("안녕하세요"), AIMessage("반갑습니다!")]
```

리듀서가 없는 필드(예: `intent: str`)는 노드가 반환한 값으로 **덮어쓰기** 됩니다.

### START, END 특수 노드

LangGraph는 두 개의 특수 노드를 제공합니다.

| 노드 | 역할 |
|------|------|
| `START` | 그래프 실행의 시작점. 입력 데이터가 여기서 상태로 변환됩니다 |
| `END` | 그래프 실행의 종료점. 이 노드에 도달하면 최종 상태를 반환합니다 |

### 노드와 엣지 추가

노드는 상태를 받아 상태의 일부를 반환하는 **일반 함수**입니다. 엣지는 노드 간의 연결을 정의합니다.

```python
# node_edge_example.py -- 노드와 엣지의 기본 사용법
from langgraph.graph import StateGraph, START, END

class SimpleState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    step: str

def greet(state: SimpleState) -> dict:
    return {"step": "greeted"}

def respond(state: SimpleState) -> dict:
    return {"step": "responded"}

graph = StateGraph(SimpleState)
graph.add_node("greet", greet)       # 노드 추가
graph.add_node("respond", respond)   # 노드 추가
graph.add_edge(START, "greet")       # START → greet
graph.add_edge("greet", "respond")   # greet → respond
graph.add_edge("respond", END)       # respond → END
app = graph.compile()
```

### 조건부 엣지: add_conditional_edges

조건부 엣지는 런타임에 상태를 검사하여 다음 노드를 동적으로 결정합니다.

```python
# conditional_edge_example.py -- 조건부 엣지로 동적 라우팅
from langchain_core.messages import AIMessage

def route_by_intent(state: SimpleState) -> str:
    """상태의 intent에 따라 다음 노드를 결정합니다."""
    last_message = state["messages"][-1]

    # AIMessage에 tool_calls가 있으면 도구 실행 노드로
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    # 그렇지 않으면 종료
    return "end"

# 조건부 엣지 추가
graph.add_conditional_edges(
    "llm_node",          # 출발 노드
    route_by_intent,     # 라우팅 함수
    {
        "tools": "tool_node",  # "tools" 반환 시 → tool_node
        "end": END,            # "end" 반환 시 → END
    }
)
```

### 코드 예제: 간단한 챗봇 StateGraph

아래는 OpenAI GPT-4o를 사용하는 가장 기본적인 StateGraph 챗봇입니다.

```python
# simple_chatbot.py -- StateGraph 기반 간단한 챗봇
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

def chatbot_node(state: ChatState) -> dict:
    """LLM에 메시지를 전달하고 응답을 받습니다."""
    return {"messages": [llm.invoke(state["messages"])]}

# 그래프 구성 → 컴파일 → 실행
graph = StateGraph(ChatState)
graph.add_node("chatbot", chatbot_node)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="LangGraph가 뭐야?")]})
print(result["messages"][-1].content)
```

### StateGraph 구조 다이어그램

```mermaid
flowchart TB
    S["START"] --> A["노드 A<br/>상태 처리"]
    A --> B{"조건부 엣지<br/>route_function()"}
    B -->|"조건 1"| C["노드 B - 도구 실행"]
    B -->|"조건 2"| D["노드 C - 사용자 확인"]
    B -->|"조건 3"| E["END"]
    C --> A
    D --> A

    subgraph State["TypedDict 상태"]
        direction LR
        S1["messages: list"] ~~~ S2["intent: str"] ~~~ S3["data: dict"]
    end

    style S fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style A fill:#0984e3,stroke:#74b9ff,color:#fff
    style B fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style C fill:#e17055,stroke:#fab1a0,color:#fff
    style D fill:#fd79a8,stroke:#e84393,color:#fff
    style E fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style S1 fill:#00b894,stroke:#55efc4,color:#fff
    style S2 fill:#00b894,stroke:#55efc4,color:#fff
    style S3 fill:#00b894,stroke:#55efc4,color:#fff
    style State fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

> **핵심 포인트:** StateGraph의 핵심은 세 가지입니다. (1) TypedDict로 상태를 명시적으로 정의하고, (2) 노드 함수는 상태를 받아 업데이트할 부분만 반환하며, (3) 조건부 엣지로 런타임에 실행 경로를 동적으로 결정합니다.

---

## 3. 체크포인팅과 메모리

### 왜 체크포인팅이 필요한가

일반적인 체인은 실행이 끝나면 모든 상태가 사라집니다. 그러나 실제 에이전트는 **대화 연속성**(이전 맥락 기억), **실행 재개**(중단 지점부터 복원), **상태 감사**(사고 과정 추적), **멀티 세션**(사용자별 독립 관리)이 필요합니다. LangGraph는 **체크포인터(Checkpointer)** 를 통해 이 모든 것을 해결합니다.

### MemorySaver (인메모리)

가장 간단한 체크포인터는 `MemorySaver`입니다. 메모리에 상태를 저장하므로 프로세스가 종료되면 데이터가 사라지지만, 개발과 테스트에 적합합니다.

```python
# memory_saver_example.py -- MemorySaver를 사용한 인메모리 체크포인팅
from langgraph.checkpoint.memory import MemorySaver

# 체크포인터 생성
memory = MemorySaver()

# 그래프 컴파일 시 체크포인터 연결
app = graph.compile(checkpointer=memory)

# 실행 시 thread_id로 대화 세션 구분
config = {"configurable": {"thread_id": "user-123"}}

# 첫 번째 메시지
result1 = app.invoke(
    {"messages": [HumanMessage(content="내 이름은 수현이야")]},
    config=config
)

# 두 번째 메시지 (같은 thread_id → 이전 대화 기억)
result2 = app.invoke(
    {"messages": [HumanMessage(content="내 이름이 뭐라고 했지?")]},
    config=config
)

print(result2["messages"][-1].content)
# 출력: "당신의 이름은 수현이라고 하셨습니다."
```

### SqliteSaver (영속 저장)

프로덕션 환경에서는 `SqliteSaver`나 `PostgresSaver`를 사용하여 상태를 영속적으로 저장합니다.

```python
# sqlite_saver_example.py -- SqliteSaver를 사용한 영속 체크포인팅
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# SQLite 데이터베이스 연결
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
saver = SqliteSaver(conn)

# 그래프 컴파일
app = graph.compile(checkpointer=saver)

# 서버 재시작 후에도 대화 이력이 유지됩니다
config = {"configurable": {"thread_id": "session-abc"}}
result = app.invoke(
    {"messages": [HumanMessage(content="지난번에 이야기하던 것 계속하자")]},
    config=config
)
```

PostgreSQL을 사용하는 프로덕션 환경에서는 `PostgresSaver`를 사용합니다.

```python
# postgres_saver_example.py -- PostgresSaver 프로덕션 설정
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:password@localhost:5432/langgraph_db"

with PostgresSaver.from_conn_string(DB_URI) as saver:
    saver.setup()  # 필요한 테이블 자동 생성
    app = graph.compile(checkpointer=saver)
```

### thread_id로 대화 분리

`thread_id`는 대화 세션을 구분하는 고유 식별자입니다. 같은 그래프 인스턴스에서 여러 사용자의 대화를 독립적으로 관리할 수 있습니다. 사용자 A의 `thread_id`와 사용자 B의 `thread_id`가 다르면 대화는 완전히 독립적으로 유지됩니다.

### 상태 스냅샷 조회

체크포인터를 사용하면 `get_state`로 현재 상태를, `get_state_history`로 과거 체크포인트 이력을 조회할 수 있습니다.

```python
# state_snapshot_example.py -- 상태 스냅샷 조회
config = {"configurable": {"thread_id": "user-123"}}

# 현재 상태 조회
current_state = app.get_state(config)
print("현재 메시지 수:", len(current_state.values["messages"]))
print("다음 노드:", current_state.next)

# 상태 이력 조회
for snapshot in app.get_state_history(config):
    print(f"체크포인트: {snapshot.config['configurable']['checkpoint_id']}")
```

### 코드 예제: 체크포인팅이 있는 대화형 에이전트

```python
# conversational_agent.py -- 체크포인팅을 활용한 완전한 대화형 에이전트
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


class ConversationState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
SYSTEM_PROMPT = SystemMessage(content="당신은 친절한 한국어 AI 어시스턴트입니다.")


def chat_node(state: ConversationState) -> dict:
    """시스템 프롬프트를 포함하여 LLM을 호출합니다."""
    messages = [SYSTEM_PROMPT] + state["messages"]
    return {"messages": [llm.invoke(messages)]}


# 그래프 구성 + 체크포인터 연결
graph = StateGraph(ConversationState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)


# 대화 루프
def main():
    config = {"configurable": {"thread_id": "demo-session"}}
    print("대화형 에이전트 (종료: quit)")

    while True:
        user_input = input("\n사용자: ")
        if user_input.lower() == "quit":
            break
        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        print(f"AI: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
```

> **핵심 포인트:** 체크포인팅은 LangGraph 에이전트의 "기억"을 담당합니다. `thread_id`로 세션을 분리하고, `get_state`/`get_state_history`로 에이전트의 사고 과정을 추적할 수 있습니다. 개발에는 `MemorySaver`, 프로덕션에는 `PostgresSaver`를 사용하세요.

---

## 4. ReAct 에이전트

### ReAct 패턴이란

ReAct(Reasoning + Acting)는 LLM이 **사고(Reasoning)** 와 **행동(Acting)** 을 번갈아 수행하는 에이전트 패턴입니다. LLM이 질문을 분석하고, 필요한 도구를 호출하고, 도구 결과를 관찰한 뒤, 다시 사고하여 최종 답변을 생성합니다.

이 패턴의 핵심은 **순환(Cycle)** 입니다. LLM이 도구를 호출하면 도구 노드에서 실행 후 결과를 다시 LLM 노드로 보내는 루프가 형성됩니다.

### create_react_agent() 유틸리티

LangGraph는 ReAct 에이전트를 한 줄로 만들 수 있는 유틸리티 함수를 제공합니다.

```python
# create_react_simple.py -- create_react_agent 빠른 시작
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")
tools = [my_tool_1, my_tool_2]

# 한 줄로 ReAct 에이전트 생성
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("human", "서울 날씨 알려줘")]})
```

그러나 실무에서는 커스텀 로직이 필요한 경우가 많으므로, StateGraph로 직접 구성하는 방법을 익히는 것이 중요합니다.

### @tool 데코레이터로 도구 정의

LangChain의 `@tool` 데코레이터로 도구를 정의합니다. 도구의 이름, 설명(docstring), 파라미터 타입이 LLM에 전달되어 적절한 도구 선택과 인자 생성에 사용됩니다.

```python
# tool_definitions.py -- @tool 데코레이터로 도구 정의
from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """웹에서 최신 정보를 검색합니다. 실시간 정보가 필요할 때 사용하세요."""
    # 실제로는 Tavily, Serper 등의 검색 API 사용
    return f"'{query}' 검색 결과: 관련 정보를 수집했습니다."


@tool
def calculate(expression: str) -> str:
    """수학 계산을 수행합니다. 사칙연산, 제곱 등을 지원합니다."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"계산 오류: {e}"


@tool
def get_current_time() -> str:
    """현재 날짜와 시간을 반환합니다."""
    from datetime import datetime
    return datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
```

### ToolNode: 도구 실행 노드

`ToolNode`는 LLM이 생성한 `tool_calls`를 실제로 실행하는 노드입니다. LLM의 응답에 포함된 도구 호출 정보를 파싱하고, 해당 도구를 실행한 뒤 결과를 `ToolMessage`로 반환합니다.

```python
# tool_node_example.py -- ToolNode 사용법
from langgraph.prebuilt import ToolNode

tools = [search_web, calculate, get_current_time]

# ToolNode는 도구 리스트를 받아 자동으로 실행합니다
tool_node = ToolNode(tools)
```

### Human-in-the-Loop

에이전트가 위험한 작업(결제, 데이터 삭제 등)을 수행하기 전에 사용자의 확인을 받아야 하는 경우가 있습니다. LangGraph의 `interrupt_before`와 `interrupt_after`를 사용하면 특정 노드 실행 전후에 그래프를 일시 중단할 수 있습니다. 중단된 그래프는 `app.invoke(None, config)`로 재개합니다.

### 코드 예제: 검색+계산기 ReAct 에이전트

```python
# react_agent_full.py -- 검색+계산기 ReAct 에이전트 with Human-in-the-Loop
from typing import Annotated, TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

class ReActState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    return f"'{query}' 검색 결과: 관련 정보를 찾았습니다."

@tool
def calculate(expression: str) -> str:
    """수학 계산을 수행합니다."""
    try:
        return f"계산 결과: {eval(expression, {'__builtins__': {}})}"
    except Exception as e:
        return f"계산 오류: {e}"

tools = [search_web, calculate]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: ReActState) -> dict:
    """LLM이 사고하고 도구 호출 여부를 결정합니다."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: ReActState) -> Literal["tools", "end"]:
    """도구 호출이 있으면 tools, 없으면 end로 라우팅."""
    last = state["messages"][-1]
    return "tools" if isinstance(last, AIMessage) and last.tool_calls else "end"

# 그래프 구성
graph = StateGraph(ReActState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
graph.add_edge("tools", "agent")  # 순환: 도구 결과 → 다시 에이전트

# Human-in-the-Loop: 도구 실행 전 사용자 확인
app = graph.compile(checkpointer=MemorySaver(), interrupt_before=["tools"])

# 실행
config = {"configurable": {"thread_id": "react-demo"}}
result = app.invoke(
    {"messages": [HumanMessage(content="한국 GDP 검색 후 1.03 곱해줘")]},
    config=config
)

# 중단된 상태에서 사용자 승인 후 재개
state = app.get_state(config)
if state.next:
    print(f"도구 호출 대기: {state.values['messages'][-1].tool_calls}")
    result = app.invoke(None, config=config)  # 승인 후 재개
print(result["messages"][-1].content)
```

### ReAct 에이전트 그래프 구조

```mermaid
flowchart LR
    S["START"] --> A["Agent 노드\nLLM 사고 + 판단"]
    A -->|"tool_calls 있음"| H{"Human-in-the-Loop\n사용자 승인?"}
    H -->|"승인"| T["Tools 노드\n도구 실행"]
    H -->|"거부"| E["END"]
    T -->|"결과 반환"| A
    A -->|"tool_calls 없음\n(최종 응답)"| E

    style S fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style A fill:#0984e3,stroke:#74b9ff,color:#fff
    style H fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style T fill:#e17055,stroke:#fab1a0,color:#fff
    style E fill:#6c5ce7,stroke:#a29bfe,color:#fff
```

> **핵심 포인트:** ReAct 에이전트의 핵심은 LLM 노드와 Tool 노드 사이의 **순환 루프**입니다. LLM은 도구가 더 이상 필요 없다고 판단할 때까지 "사고 → 도구 호출 → 결과 관찰"을 반복합니다. `interrupt_before`를 사용하면 민감한 작업 전에 사용자 확인을 받을 수 있습니다.

---

## 5. 멀티 에이전트

### 왜 멀티 에이전트인가

하나의 에이전트에 모든 도구와 책임을 부여하면 다음과 같은 문제가 발생합니다.

| 문제 | 설명 |
|------|------|
| 도구 혼란 | 도구가 많아지면 LLM이 적절한 도구를 선택하지 못합니다 |
| 프롬프트 비대화 | 시스템 프롬프트가 길어져 성능이 저하됩니다 |
| 전문성 부족 | 하나의 프롬프트로 다양한 전문 분야를 커버하기 어렵습니다 |
| 디버깅 어려움 | 어떤 부분이 실패했는지 파악하기 힘듭니다 |

멀티 에이전트는 각 에이전트에 **명확한 역할과 전문 도구**를 부여하여 이 문제를 해결합니다.

### Supervisor 패턴

Supervisor 패턴은 **중앙 관리자(Supervisor)** 가 사용자 요청을 분석하고 적절한 **워커(Worker) 에이전트**에 작업을 위임하는 구조입니다.

Supervisor는 상태에 `next_worker` 필드를 두고, 라우팅 함수가 이 값을 기반으로 다음 워커 노드를 선택합니다. 각 워커가 작업을 완료하면 다시 Supervisor로 돌아와 다음 작업을 결정합니다.

### Handoff 패턴

Handoff 패턴은 에이전트 간에 **직접 전달(Handoff)** 이 이루어지는 구조입니다. Supervisor 없이 에이전트가 자신의 역할 범위를 벗어나는 요청을 받으면 `transfer_to_*` 도구를 호출하여 다른 에이전트에게 작업을 넘깁니다. 각 에이전트는 `@tool(return_direct=True)`로 정의된 전달 도구를 보유합니다.

### 코드 예제: Supervisor + 2 Worker 에이전트

아래는 Supervisor가 리서치 에이전트와 코딩 에이전트를 관리하는 완전한 예제입니다.

```python
# multi_agent_supervisor.py -- Supervisor + Worker 멀티 에이전트 시스템
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import json


# --- 1. 상태 정의 ---
class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str


# --- 2. 도구 정의 ---
@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    return f"'{query}'에 대한 검색 결과를 수집했습니다."

@tool
def write_code(spec: str) -> str:
    """요구사항에 맞는 코드를 작성합니다."""
    return f"코드 작성 완료: {spec}"


# --- 3. LLM 초기화 ---
llm = ChatOpenAI(model="gpt-4o", temperature=0)


# --- 4. Supervisor 노드 ---
def supervisor_node(state: MultiAgentState) -> dict:
    """작업을 분석하고 적절한 워커에게 위임합니다."""
    messages = [
        SystemMessage(content=(
            "당신은 팀 관리자입니다. 워커를 선택하세요.\n"
            "- researcher: 정보 검색, 조사\n"
            "- coder: 코드 작성, 프로그래밍\n"
            "- FINISH: 모든 작업 완료\n"
            'JSON 형식: {"next": "worker_name"}'
        ))
    ] + state["messages"]

    response = llm.invoke(messages)
    try:
        next_agent = json.loads(response.content).get("next", "FINISH")
    except json.JSONDecodeError:
        next_agent = "FINISH"

    return {
        "next_agent": next_agent,
        "messages": [AIMessage(content=f"[Supervisor] 다음 워커: {next_agent}")]
    }


# --- 5. Worker 노드 ---
def researcher_node(state: MultiAgentState) -> dict:
    """리서치 작업을 수행합니다."""
    llm_with_tools = llm.bind_tools([search_web])
    messages = [SystemMessage(content="리서치 전문 에이전트입니다.")] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [AIMessage(content=f"[Researcher] {response.content}")]}


def coder_node(state: MultiAgentState) -> dict:
    """코딩 작업을 수행합니다."""
    llm_with_tools = llm.bind_tools([write_code])
    messages = [SystemMessage(content="코딩 전문 에이전트입니다.")] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [AIMessage(content=f"[Coder] {response.content}")]}


# --- 6. 라우팅 + 그래프 구성 ---
def route_supervisor(state: MultiAgentState) -> str:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent in ("researcher", "coder"):
        return next_agent
    return "end"


graph = StateGraph(MultiAgentState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("coder", coder_node)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor", route_supervisor,
    {"researcher": "researcher", "coder": "coder", "end": END}
)
graph.add_edge("researcher", "supervisor")  # 워커 완료 → Supervisor
graph.add_edge("coder", "supervisor")       # 워커 완료 → Supervisor

app = graph.compile()

# --- 7. 실행 ---
result = app.invoke({
    "messages": [HumanMessage(content="피보나치 수열 생성기를 만들고, 자연에서의 사례도 조사해줘")],
    "next_agent": ""
})
for msg in result["messages"]:
    print(f"{msg.content[:80]}...")
```

### 멀티 에이전트 Supervisor 아키텍처

```mermaid
flowchart LR
    U["사용자 요청"] --> S["Supervisor\n작업 분석 및 위임"]
    S -->|"정보 검색 필요"| R["Researcher Agent\n검색 + 분석"]
    S -->|"코드 작성 필요"| C["Coder Agent\n코딩 + 리뷰"]
    S -->|"모든 작업 완료"| E["END\n최종 응답 반환"]
    R --> S
    C --> S

    subgraph ResearcherTools["Researcher 도구"]
        RT1["search_web\n웹 검색"]
        RT2["analyze_data\n데이터 분석"]
    end

    subgraph CoderTools["Coder 도구"]
        CT1["write_code\n코드 작성"]
        CT2["review_code\n코드 리뷰"]
    end

    R -.-> ResearcherTools
    C -.-> CoderTools

    style U fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style S fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style R fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#00b894,stroke:#55efc4,color:#fff
    style E fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style RT1 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style RT2 fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style CT1 fill:#55efc4,stroke:#00b894,color:#2d3436
    style CT2 fill:#55efc4,stroke:#00b894,color:#2d3436
    style ResearcherTools fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style CoderTools fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

> **핵심 포인트:** 멀티 에이전트 시스템은 복잡한 작업을 전문화된 에이전트로 분할하여 처리합니다. Supervisor 패턴은 중앙 관리자가 작업을 분배하고, Handoff 패턴은 에이전트 간 직접 전달이 이루어집니다. 실무에서는 도구가 5개를 넘어가면 멀티 에이전트를 고려하세요.

---

## 6. 스트리밍과 디버깅

### 스트리밍이 필요한 이유

에이전트가 여러 도구를 호출하며 작업하면 최종 응답까지 수십 초가 걸릴 수 있습니다. 사용자에게 빈 화면을 보여주는 것보다 **실시간으로 진행 상황을 전달**하는 것이 훨씬 좋은 사용자 경험을 제공합니다.

### stream_mode 옵션

LangGraph는 세 가지 스트리밍 모드를 제공합니다.

| stream_mode | 설명 | 사용 사례 |
|-------------|------|-----------|
| `"values"` | 각 노드 실행 후 전체 상태를 반환 | 전체 상태 변화 추적 |
| `"updates"` | 각 노드가 변경한 부분만 반환 | 효율적인 변경 사항 추적 |
| `"messages"` | LLM 토큰 단위 스트리밍 | 실시간 타이핑 효과 |

```python
# streaming_modes.py -- 세 가지 스트리밍 모드 비교
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "stream-demo"}}
input_msg = {"messages": [HumanMessage(content="파이썬에 대해 알려줘")]}

# 1. values 모드: 각 노드 실행 후 전체 상태 스냅샷
for state_snapshot in app.stream(input_msg, config, stream_mode="values"):
    if "messages" in state_snapshot:
        print(f"[{type(state_snapshot['messages'][-1]).__name__}] ...")

# 2. updates 모드: 노드별 변경 사항만
for node_name, update in app.stream(input_msg, config, stream_mode="updates"):
    print(f"노드 '{node_name}'가 업데이트")

# 3. messages 모드: 토큰 단위 스트리밍 (실시간 타이핑 효과)
for msg, metadata in app.stream(input_msg, config, stream_mode="messages"):
    if hasattr(msg, "content") and msg.content:
        print(msg.content, end="", flush=True)
```

### astream_events (비동기 이벤트 스트리밍)

더 세밀한 제어가 필요하면 `astream_events`를 사용합니다. 이 API는 LLM 호출, 도구 실행 등 개별 이벤트를 비동기적으로 스트리밍합니다.

```python
# astream_events_example.py -- astream_events로 세밀한 이벤트 스트리밍
import asyncio
from langchain_core.messages import HumanMessage


async def stream_with_events():
    config = {"configurable": {"thread_id": "events-demo"}}
    input_msg = {"messages": [HumanMessage(content="검색하고 계산해줘")]}

    async for event in app.astream_events(input_msg, config, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)
        elif kind == "on_tool_start":
            print(f"\n[도구 실행 중] {event['name']}")
        elif kind == "on_tool_end":
            print(f"  결과: {str(event['data'].output)[:50]}...")

asyncio.run(stream_with_events())
```

### LangGraph Studio 소개

**LangGraph Studio**는 LangGraph 에이전트를 시각적으로 디버깅하고 테스트할 수 있는 데스크톱 도구입니다. LangSmith와 통합되어 있으며, 그래프의 실행 과정을 실시간으로 시각화합니다.

주요 기능은 다음과 같습니다.

| 기능 | 설명 |
|------|------|
| 그래프 시각화 | 노드와 엣지를 시각적으로 표시 |
| 실시간 실행 추적 | 각 노드의 입출력을 실시간으로 확인 |
| 상태 편집 | 중간 상태를 수정하고 재실행 |
| 브레이크포인트 | 특정 노드에서 실행을 멈추고 상태 검사 |
| 타임 트래블 | 이전 체크포인트로 돌아가 재실행 |

LangSmith에서 추적을 활성화하려면 환경 변수를 설정합니다.

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__your_api_key"
export LANGCHAIN_PROJECT="my-langgraph-agent"
```

### 코드 예제: FastAPI + LangGraph 스트리밍

```python
# fastapi_streaming.py -- FastAPI와 LangGraph 스트리밍 통합
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json

app_api = FastAPI()

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app_api.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE(Server-Sent Events)로 에이전트 응답을 스트리밍합니다."""
    async def event_generator():
        config = {"configurable": {"thread_id": request.thread_id}}
        input_msg = {"messages": [HumanMessage(content=request.message)]}

        async for event in app.astream_events(input_msg, config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'type': 'tool_start', 'name': event['name']})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# uvicorn fastapi_streaming:app_api --reload --port 8000
```

> **핵심 포인트:** 스트리밍은 에이전트의 사용자 경험을 극적으로 개선합니다. `stream_mode="messages"`로 토큰 단위 스트리밍을, `astream_events`로 도구 실행 상태까지 전달할 수 있습니다. LangSmith와 LangGraph Studio를 활용하면 에이전트의 실행 과정을 시각적으로 디버깅할 수 있습니다.

---

## 7. 고급 패턴

### 서브그래프: 그래프 안의 그래프

복잡한 에이전트 시스템에서는 하나의 거대한 그래프 대신 **서브그래프(Subgraph)** 를 사용하여 모듈화합니다. 서브그래프는 독립적으로 테스트하고 재사용할 수 있습니다.

```python
# subgraph_example.py -- 서브그래프를 사용한 모듈화
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


# --- 서브그래프: 리서치 파이프라인 ---
class ResearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    research_result: str

def search_node(state: ResearchState) -> dict:
    return {"research_result": f"'{state['messages'][-1].content}' 검색 결과"}

def summarize_node(state: ResearchState) -> dict:
    return {
        "messages": [AIMessage(content=f"요약: {state.get('research_result', '')}")],
        "research_result": f"요약 완료"
    }

research_graph = StateGraph(ResearchState)
research_graph.add_node("search", search_node)
research_graph.add_node("summarize", summarize_node)
research_graph.add_edge(START, "search")
research_graph.add_edge("search", "summarize")
research_graph.add_edge("summarize", END)
research_subgraph = research_graph.compile()


# --- 메인 그래프: 서브그래프를 노드로 사용 ---
class MainState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    research_result: str

def coordinator_node(state: MainState) -> dict:
    return {"messages": [AIMessage(content=f"최종: {state.get('research_result', '')}")]}

main_graph = StateGraph(MainState)
main_graph.add_node("research", research_subgraph)  # 서브그래프를 노드로 추가
main_graph.add_node("coordinator", coordinator_node)
main_graph.add_edge(START, "research")
main_graph.add_edge("research", "coordinator")
main_graph.add_edge("coordinator", END)

main_app = main_graph.compile()
result = main_app.invoke({"messages": [HumanMessage(content="AI 트렌드 조사")], "research_result": ""})
```

### 맵-리듀스: 병렬 처리 후 결과 합침

여러 작업을 **병렬로 실행**하고 결과를 합치는 맵-리듀스 패턴은 다수의 문서를 동시에 분석하거나, 여러 소스에서 정보를 수집할 때 유용합니다.

```python
# map_reduce_example.py -- Send API를 사용한 맵-리듀스 패턴
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator

class MapReduceState(TypedDict):
    topics: list[str]
    results: Annotated[list[str], operator.add]
    final_summary: str

class SingleTopicState(TypedDict):
    topic: str
    results: Annotated[list[str], operator.add]

def distribute_topics(state: MapReduceState) -> list[Send]:
    """각 주제를 개별 분석 노드로 분배합니다 (Map)."""
    return [Send("analyze", {"topic": t, "results": []}) for t in state["topics"]]

def analyze_topic(state: SingleTopicState) -> dict:
    """개별 주제를 분석합니다 (실제로는 LLM 호출)."""
    return {"results": [f"{state['topic']} 분석 결과"]}

def reduce_results(state: MapReduceState) -> dict:
    """모든 분석 결과를 종합합니다 (Reduce)."""
    return {"final_summary": "\n".join(f"- {r}" for r in state.get("results", []))}

graph = StateGraph(MapReduceState)
graph.add_node("analyze", analyze_topic)
graph.add_node("reduce", reduce_results)
graph.add_conditional_edges(START, distribute_topics)
graph.add_edge("analyze", "reduce")
graph.add_edge("reduce", END)

result = graph.compile().invoke({
    "topics": ["AI 트렌드", "클라우드 컴퓨팅", "사이버 보안"], "results": [], "final_summary": ""
})
```

### 서브그래프와 맵-리듀스 아키텍처

```mermaid
flowchart LR
    subgraph MainGraph["메인 그래프"]
        direction LR
        S["START"] --> SG["서브그래프"] --> CO["Coordinator"] --> E["END"]
    end

    subgraph SubGraph["서브그래프 내부"]
        direction LR
        SS["START"] --> SE["Search"] --> SU["Summarize"] --> SE2["END"]
    end

    subgraph MapReduce["맵-리듀스 패턴"]
        direction LR
        MS["START"] --> D{"distribute"}
        D -->|"주제 1"| A1["Analyze 1"]
        D -->|"주제 2"| A2["Analyze 2"]
        D -->|"주제 3"| A3["Analyze 3"]
        A1 --> R["Reduce"]
        A2 --> R
        A3 --> R
        R --> ME["END"]
    end

    style S fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style SG fill:#0984e3,stroke:#74b9ff,color:#fff
    style CO fill:#00b894,stroke:#55efc4,color:#fff
    style E fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style SS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style SE fill:#0984e3,stroke:#74b9ff,color:#fff
    style SU fill:#0984e3,stroke:#74b9ff,color:#fff
    style SE2 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style MS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style A1 fill:#e17055,stroke:#fab1a0,color:#fff
    style A2 fill:#e17055,stroke:#fab1a0,color:#fff
    style A3 fill:#e17055,stroke:#fab1a0,color:#fff
    style R fill:#fd79a8,stroke:#e84393,color:#fff
    style ME fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style MainGraph fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style SubGraph fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style MapReduce fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 타임아웃과 에러 복구

프로덕션 에이전트는 무한 루프 방지와 에러 처리가 필수적입니다.

```python
# error_handling.py -- 타임아웃과 에러 복구 패턴
from langgraph.errors import GraphRecursionError

# 1. 재귀 제한: 무한 루프 방지
try:
    result = app.invoke(
        {"messages": [HumanMessage(content="복잡한 작업")]},
        config={"recursion_limit": 25}  # 최대 25번 노드 실행
    )
except GraphRecursionError:
    print("에이전트가 최대 반복 횟수를 초과했습니다.")


# 2. 노드 내부 에러 처리
def safe_tool_node(state):
    """에러를 안전하게 처리하는 도구 노드."""
    try:
        result = risky_tool.invoke(state["messages"][-1].tool_calls)
        return {"messages": [result]}
    except (TimeoutError, Exception) as e:
        return {"messages": [AIMessage(content=f"도구 실행 오류: {e}")]}


# 3. 반복 횟수 기반 중단
def agent_with_limit(state):
    """반복 횟수를 추적하여 무한 루프를 방지합니다."""
    iteration = state.get("iteration_count", 0) + 1
    if iteration > 10:
        return {"messages": [AIMessage(content="최대 시도 횟수 도달")], "iteration_count": iteration}
    response = llm.invoke(state["messages"])
    return {"messages": [response], "iteration_count": iteration}
```

> **핵심 포인트:** 서브그래프로 복잡한 에이전트를 모듈화하고, 맵-리듀스로 병렬 처리를 구현하며, 재귀 제한과 에러 처리로 프로덕션 안정성을 확보하세요. `recursion_limit`은 무한 루프 방지의 마지막 방어선입니다.

---

## 8. 핵심 정리

### LangGraph 패턴 정리표

| 패턴 | 설명 | 핵심 API | 사용 사례 |
|------|------|----------|-----------|
| StateGraph 기본 | TypedDict 상태 + 노드 + 엣지 | `StateGraph`, `add_node`, `add_edge` | 모든 LangGraph 앱의 기초 |
| 조건부 엣지 | 런타임에 다음 노드를 동적 결정 | `add_conditional_edges` | 도구 호출 여부 판단, 라우팅 |
| 체크포인팅 | 상태 영속성, 대화 기억 | `MemorySaver`, `SqliteSaver` | 대화형 에이전트, 멀티 턴 |
| ReAct 에이전트 | 사고 → 행동 → 관찰 순환 루프 | `create_react_agent`, `ToolNode` | 도구 사용 에이전트 |
| Human-in-the-Loop | 사용자 확인 후 실행 재개 | `interrupt_before`, `interrupt_after` | 결제, 데이터 삭제 등 민감 작업 |
| Supervisor 멀티 에이전트 | 중앙 관리자가 워커에 작업 위임 | `StateGraph` + 라우팅 함수 | 복잡한 멀티 도메인 작업 |
| Handoff 멀티 에이전트 | 에이전트 간 직접 전달 | `transfer_to_*` 도구 | 에이전트 간 유연한 협력 |
| 서브그래프 | 그래프를 노드로 중첩 사용 | `compiled_graph`를 `add_node`에 전달 | 복잡한 파이프라인 모듈화 |
| 맵-리듀스 | 병렬 실행 후 결과 합침 | `Send` API | 다수 문서 분석, 병렬 검색 |
| 스트리밍 | 실시간 진행 상황 전달 | `stream`, `astream_events` | 사용자 경험 향상 |

### 핵심 설계 원칙

1. **상태를 명시적으로 정의하세요** — TypedDict로 에이전트가 다루는 모든 데이터를 선언합니다
2. **리듀서를 적절히 사용하세요** — `add_messages`로 메시지를 누적하고, 단순 필드는 덮어쓰기를 사용합니다
3. **순환은 제한과 함께 사용하세요** — `recursion_limit`으로 무한 루프를 방지합니다
4. **체크포인팅은 필수입니다** — 대화형 에이전트라면 반드시 체크포인터를 연결하세요
5. **도구가 5개를 넘으면 멀티 에이전트를 고려하세요** — 전문화된 에이전트가 범용 에이전트보다 정확합니다
6. **LangSmith로 추적하세요** — 에이전트의 사고 과정을 추적하지 않으면 디버깅이 불가능합니다

### 핵심 의존성 요약

```bash
# 핵심 패키지
pip install langgraph>=0.2.0        # LangGraph 코어
pip install langchain-openai         # OpenAI 통합
pip install langsmith                # 추적 및 디버깅

# 체크포인터 (필요에 따라 선택)
pip install langgraph-checkpoint-sqlite    # SQLite 영속 저장
pip install langgraph-checkpoint-postgres  # PostgreSQL 영속 저장

# 추가 도구
pip install tavily-python            # 웹 검색 도구
pip install langchain-community      # 커뮤니티 도구 모음
```

> **핵심 포인트:** LangGraph는 "상태 + 노드 + 엣지"라는 단순한 추상화 위에 체크포인팅, 스트리밍, Human-in-the-Loop, 멀티 에이전트 등 강력한 기능을 제공합니다. 작은 StateGraph부터 시작하여 점진적으로 복잡성을 추가하는 것이 가장 효과적인 학습 방법입니다.

---

다음 강의에서는 **MCP(Model Context Protocol)**를 다룹니다. AI 모델이 외부 도구와 데이터 소스를 표준화된 프로토콜로 연결하는 방법, MCP 서버 구현, 그리고 에이전트와 MCP를 통합하는 실전 기법을 배웁니다.
