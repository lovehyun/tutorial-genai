"""
Agentic RAG — 에이전트가 검색 전략을 능동적으로 결정.
이 예제: 검색 필요성 판단 + 쿼리 재작성 + 결과 충분성 평가를 LangGraph 로 구현.

기존 RAG:    질문 → (무조건) 검색 → 응답
Agentic RAG: 질문 → 필요하면 검색 → 부족하면 재검색 → 응답

  ※ pip install langgraph


─── 그래프 구조 ─────────────────────────────────────────────

                       ┌───────────┐
                       │   START   │
                       └─────┬─────┘
                             │
                             ▼
                       ┌───────────┐
                       │  assess   │   외부 문서 검색이 필요한 질문인가?
                       └─────┬─────┘   (인사/일반 대화면 곧장 generate)
                             │
                ┌────────────┴────────────┐
        needs=True │                       │ needs=False
                   ▼                       │
              ┌─────────┐                  │
       ┌────► │ rewrite │ 검색용 쿼리      │
       │      └────┬────┘  재작성          │
       │           │                       │
       │           ▼                       │
       │      ┌──────────┐                 │
       │      │ retrieve │ 벡터 DB 검색    │
       │      └────┬─────┘                 │
       │           │                       │
       │           ▼                       │
       │      ┌──────────┐                 │
       │      │ evaluate │ 결과 충분?      │
       │      └────┬─────┘                 │
       │           │                       │
       │ ┌─────────┴─────────┐             │
       │ │                   │             │
       │ insufficient        sufficient    │
       │ AND iter < 2        OR  iter ≥ 2  │
       │ │                   │             │
       └─┘ (다시 재작성)     │             │
                             ▼             │
                       ┌──────────┐        │
                       │ generate │ ◄──────┘
                       └────┬─────┘
                            │
                            ▼
                       ┌──────────┐
                       │   END    │
                       └──────────┘

흐름 요약:
  1) assess           → 검색이 필요한 질문인지 LLM 이 한 단어로 판정
  2) (필요 없으면) generate 로 바로 가서 답변
  3) rewrite          → 벡터 검색에 적합한 키워드 쿼리로 재작성
  4) retrieve         → 그 쿼리로 벡터 DB 에서 top-k 가져옴
  5) evaluate         → 결과가 답하기에 충분한지 LLM 이 평가
  6) 충분하면 generate, 부족하고 iter<2 면 rewrite 로 루프백 (다른 관점 재시도)
  7) generate         → 검색된 문서를 컨텍스트로 최종 답변
"""

from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langgraph.graph import StateGraph, START, END

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 벡터 스토어 (작은 샘플) ──────────────────────────
sample_docs = [
    Document(page_content="LangChain 은 LLM 애플리케이션 프레임워크. LCEL 로 체인을 조립한다.", metadata={"src": "langchain"}),
    Document(page_content="RAG 는 외부 문서를 검색해 LLM 응답을 보강하는 기법.", metadata={"src": "rag"}),
    Document(page_content="LangGraph 는 그래프 기반 실행 엔진. 노드와 엣지로 분기/순환 구현.", metadata={"src": "langgraph"}),
    Document(page_content="ChromaDB 는 벡터 DB. 코사인 유사도로 가까운 벡터를 찾는다.", metadata={"src": "chroma"}),
]

splits = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50).split_documents(sample_docs)
store = Chroma.from_documents(splits, embedding=OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="agentic_demo")
retriever = store.as_retriever(search_kwargs={"k": 3})


# ─── 상태 정의 ────────────────────────────────────────
class State(TypedDict):
    question: str
    rewritten_query: str
    documents: List[str]
    needs_retrieval: bool
    is_sufficient: bool
    answer: str
    iteration: int


# ─── 노드들 ──────────────────────────────────────────
def assess_need(state: State) -> dict:
    """이 질문이 외부 검색을 필요로 하는가?"""
    resp = llm.invoke([
        SystemMessage(content="질문이 외부 문서 검색이 필요하면 YES, 아니면(인사/일반대화/수학 등) NO. 한 단어만."),
        HumanMessage(content=state["question"]),
    ])
    needs = "YES" in resp.content.upper()
    print(f"  [판단] 검색 필요: {'예' if needs else '아니오'}")
    return {"needs_retrieval": needs, "iteration": 0}


def rewrite_query(state: State) -> dict:
    """검색에 적합한 쿼리로 재작성 (반복 시 다른 관점으로)"""
    if state["iteration"] == 0:
        prompt = f"다음 질문을 벡터 검색용 키워드 쿼리로 재작성. 쿼리만:\n{state['question']}"
    else:
        prompt = (
            f"이전 검색이 부족했습니다. 다른 각도로 쿼리 재작성. 쿼리만.\n"
            f"질문: {state['question']}\n"
            f"이전 쿼리: {state['rewritten_query']}"
        )
    q = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    print(f"  [재작성 #{state['iteration'] + 1}] {q}")
    return {"rewritten_query": q, "iteration": state["iteration"] + 1}


def retrieve(state: State) -> dict:
    docs = retriever.invoke(state["rewritten_query"])
    print(f"  [검색] {len(docs)} 개 문서")
    return {"documents": [d.page_content for d in docs]}


def evaluate(state: State) -> dict:
    """검색 결과가 답하기에 충분한가?"""
    ctx = "\n".join(state["documents"])
    resp = llm.invoke([
        SystemMessage(content="검색 결과가 질문에 답하기 충분하면 SUFFICIENT, 아니면 INSUFFICIENT. 한 단어만."),
        HumanMessage(content=f"질문: {state['question']}\n\n결과:\n{ctx}"),
    ])
    ok = "SUFFICIENT" in resp.content.upper()
    print(f"  [평가] {'충분' if ok else '부족'}")
    return {"is_sufficient": ok}


def generate(state: State) -> dict:
    """최종 답변 생성"""
    if state["needs_retrieval"] and state["documents"]:
        ctx = "\n".join(state["documents"])
        prompt = f"참고 자료만 가지고 답하세요. 자료에 없으면 추측 금지.\n\n자료:\n{ctx}\n\n질문: {state['question']}"
    else:
        prompt = state["question"]
    return {"answer": llm.invoke([HumanMessage(content=prompt)]).content}


# ─── 분기 함수 ───────────────────────────────────────
def route_after_assess(s):
    return "rewrite" if s["needs_retrieval"] else "generate"

def route_after_eval(s):
    # 충분하거나 2번 이상 시도했으면 답변, 아니면 다시 검색
    return "generate" if (s["is_sufficient"] or s["iteration"] >= 2) else "rewrite"


# ─── 그래프 조립 ─────────────────────────────────────
g = StateGraph(State)
g.add_node("assess", assess_need)
g.add_node("rewrite", rewrite_query)
g.add_node("retrieve", retrieve)
g.add_node("evaluate", evaluate)
g.add_node("generate", generate)

g.add_edge(START, "assess")
g.add_conditional_edges("assess", route_after_assess, {"rewrite": "rewrite", "generate": "generate"})
g.add_edge("rewrite", "retrieve")
g.add_edge("retrieve", "evaluate")
g.add_conditional_edges("evaluate", route_after_eval, {"rewrite": "rewrite", "generate": "generate"})
g.add_edge("generate", END)

app = g.compile()


# ─── 실행 — 검색이 필요한 질문 vs 필요 없는 질문 비교 ──
for question in [
    "LangGraph 에서 분기는 어떻게 구현해?",  # 검색 필요
    "안녕하세요!",                          # 검색 불필요
]:
    print(f"\n=== Q: {question} ===")
    out = app.invoke({
        "question": question, "rewritten_query": "", "documents": [],
        "needs_retrieval": False, "is_sufficient": False, "answer": "", "iteration": 0,
    })
    print(f"A: {out['answer'][:200]}...")

store.delete_collection()
