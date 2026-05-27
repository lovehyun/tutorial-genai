"""
12_agentic_rag.py - Agentic RAG (에이전트 기반 RAG)

이 파일은 에이전트가 검색 전략을 능동적으로 결정하는 Agentic RAG를 구현합니다.
기존 RAG는 항상 검색→응답의 고정 파이프라인이지만,
Agentic RAG는 검색 필요성 판단, 쿼리 재작성, 검색 결과 충분성 평가를 자율적으로 수행합니다.

흐름: 질문 → 검색 필요성 판단 → 쿼리 재작성 → 검색 → 충분성 평가 → (부족 시) 재검색 → 응답
"""

from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END

load_dotenv()

print("=" * 60)
print("Agentic RAG: 에이전트가 검색 전략을 능동적으로 결정")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. 샘플 문서로 벡터 스토어 구축
# ============================================================
print("\n[준비] 벡터 스토어 구축 중...")

sample_docs = [
    Document(page_content="LangChain은 LLM 애플리케이션 개발을 위한 프레임워크입니다. LCEL(LangChain Expression Language)을 통해 체인을 구성하며, 프롬프트, 모델, 파서를 파이프 연산자로 연결합니다.", metadata={"source": "langchain_overview"}),
    Document(page_content="RAG(Retrieval-Augmented Generation)는 외부 문서를 검색하여 LLM의 응답을 보강하는 기법입니다. 임베딩으로 문서를 벡터화하고, 유사도 검색으로 관련 문서를 찾아 컨텍스트로 제공합니다.", metadata={"source": "rag_basics"}),
    Document(page_content="LangGraph는 LangChain 생태계의 그래프 기반 실행 엔진입니다. StateGraph로 노드와 엣지를 정의하고, 조건부 분기와 순환을 통해 복잡한 에이전트 워크플로우를 구현합니다.", metadata={"source": "langgraph_intro"}),
    Document(page_content="벡터 데이터베이스는 고차원 벡터를 효율적으로 저장하고 검색하는 데이터베이스입니다. ChromaDB, Pinecone, Weaviate 등이 있으며, 코사인 유사도나 유클리디안 거리로 유사한 벡터를 찾습니다.", metadata={"source": "vector_db"}),
    Document(page_content="프롬프트 엔지니어링은 LLM에 효과적인 지시를 작성하는 기술입니다. 역할 지정, 예시 제공(Few-shot), 단계별 사고(Chain-of-Thought) 등의 기법이 있습니다.", metadata={"source": "prompt_engineering"}),
    Document(page_content="에이전트(Agent)는 LLM이 도구를 사용하여 자율적으로 작업을 수행하는 시스템입니다. ReAct 패턴으로 추론(Reasoning)과 행동(Acting)을 반복하며, 도구 호출 결과를 바탕으로 다음 행동을 결정합니다.", metadata={"source": "agent_basics"}),
]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
splits = text_splitter.split_documents(sample_docs)

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    collection_name="agentic_rag_demo",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print(f"  {len(splits)}개 청크 인덱싱 완료")


# ============================================================
# 2. 상태 정의
# ============================================================
class AgenticRAGState(TypedDict):
    question: str              # 원본 질문
    rewritten_query: str       # 재작성된 검색 쿼리
    documents: List[str]       # 검색된 문서 내용
    needs_retrieval: bool      # 검색 필요 여부
    is_sufficient: bool        # 검색 결과 충분 여부
    answer: str                # 최종 답변
    iteration: int             # 검색 반복 횟수


# ============================================================
# 3. 검색 필요성 판단 노드
# ============================================================
def assess_need(state: AgenticRAGState) -> dict:
    """질문이 외부 지식(검색)을 필요로 하는지 판단합니다."""
    print(f"\n[판단] 검색 필요성 평가 중...")

    response = llm.invoke([
        SystemMessage(content="""질문이 외부 문서 검색을 필요로 하는지 판단해주세요.
검색이 필요한 경우: 특정 기술, 개념, 사실 정보에 대한 질문
검색이 불필요한 경우: 인사, 일반 대화, 수학 계산, 개인 의견

'YES' 또는 'NO'로만 답하세요."""),
        HumanMessage(content=f"질문: {state['question']}")
    ])

    needs = "YES" in response.content.upper()
    print(f"  검색 필요: {'예' if needs else '아니오'}")
    return {"needs_retrieval": needs, "iteration": 0}


# ============================================================
# 4. 쿼리 재작성 노드
# ============================================================
def rewrite_query(state: AgenticRAGState) -> dict:
    """검색에 최적화된 쿼리로 재작성합니다."""
    print(f"\n[재작성] 검색 쿼리 최적화 중... (반복 {state['iteration'] + 1})")

    if state["iteration"] == 0:
        # 첫 번째: 원본 질문 기반 재작성
        prompt = f"다음 질문을 벡터 검색에 적합한 핵심 키워드 중심의 쿼리로 재작성해주세요. 쿼리만 출력하세요.\n\n질문: {state['question']}"
    else:
        # 재검색: 이전 결과가 부족하므로 다른 관점으로 재작성
        prompt = f"""이전 검색 결과가 부족했습니다. 다른 관점에서 쿼리를 재작성해주세요.

원본 질문: {state['question']}
이전 쿼리: {state['rewritten_query']}
이전 검색 결과: {'; '.join(state['documents'][:2])}

새로운 검색 쿼리 (핵심 키워드 중심, 쿼리만 출력):"""

    response = llm.invoke([HumanMessage(content=prompt)])
    query = response.content.strip()
    print(f"  재작성된 쿼리: {query}")
    return {"rewritten_query": query, "iteration": state["iteration"] + 1}


# ============================================================
# 5. 검색 노드
# ============================================================
def retrieve(state: AgenticRAGState) -> dict:
    """벡터 스토어에서 관련 문서를 검색합니다."""
    print(f"\n[검색] '{state['rewritten_query'][:50]}' 검색 중...")

    docs = retriever.invoke(state["rewritten_query"])
    doc_contents = [doc.page_content for doc in docs]

    print(f"  {len(docs)}개 문서 검색됨")
    for i, doc in enumerate(docs, 1):
        print(f"    {i}. {doc.page_content[:60]}... [{doc.metadata.get('source', '')}]")

    return {"documents": doc_contents}


# ============================================================
# 6. 충분성 평가 노드
# ============================================================
def evaluate_sufficiency(state: AgenticRAGState) -> dict:
    """검색 결과가 질문에 답하기에 충분한지 평가합니다."""
    print(f"\n[평가] 검색 결과 충분성 평가 중...")

    context = "\n".join(state["documents"])
    response = llm.invoke([
        SystemMessage(content="""검색된 문서가 질문에 답하기에 충분한 정보를 포함하는지 평가해주세요.
'SUFFICIENT' 또는 'INSUFFICIENT'로만 답하세요."""),
        HumanMessage(content=f"질문: {state['question']}\n\n검색 결과:\n{context}")
    ])

    sufficient = "SUFFICIENT" in response.content.upper()
    print(f"  충분성: {'충분' if sufficient else '부족'}")
    return {"is_sufficient": sufficient}


# ============================================================
# 7. 응답 생성 노드
# ============================================================
def generate_answer(state: AgenticRAGState) -> dict:
    """검색 결과를 바탕으로 최종 답변을 생성합니다."""
    print(f"\n[생성] 최종 답변 생성 중...")

    if state["needs_retrieval"] and state["documents"]:
        context = "\n".join(state["documents"])
        prompt = f"""다음 참고 자료를 바탕으로 질문에 답변해주세요.
참고 자료에 없는 내용은 추측하지 마세요.

참고 자료:
{context}

질문: {state['question']}"""
    else:
        prompt = f"다음 질문에 답변해주세요.\n\n질문: {state['question']}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}


# ============================================================
# 8. 라우팅 함수
# ============================================================
def route_after_assess(state: AgenticRAGState) -> str:
    """검색 필요 여부에 따라 분기"""
    return "rewrite" if state["needs_retrieval"] else "generate"


def route_after_evaluate(state: AgenticRAGState) -> str:
    """충분성 평가 결과에 따라 분기"""
    if state["is_sufficient"] or state["iteration"] >= 2:
        if not state["is_sufficient"]:
            print(f"  최대 검색 반복(2회) 도달, 현재 결과로 응답 생성")
        return "generate"
    return "rewrite"


# ============================================================
# 9. LangGraph 그래프 구성
# ============================================================
graph = StateGraph(AgenticRAGState)

graph.add_node("assess", assess_need)
graph.add_node("rewrite", rewrite_query)
graph.add_node("retrieve", retrieve)
graph.add_node("evaluate", evaluate_sufficiency)
graph.add_node("generate", generate_answer)

graph.add_edge(START, "assess")
graph.add_conditional_edges("assess", route_after_assess, {"rewrite": "rewrite", "generate": "generate"})
graph.add_edge("rewrite", "retrieve")
graph.add_edge("retrieve", "evaluate")
graph.add_conditional_edges("evaluate", route_after_evaluate, {"generate": "generate", "rewrite": "rewrite"})
graph.add_edge("generate", END)

app = graph.compile()
print("Agentic RAG 그래프 컴파일 완료")
print("실행 흐름: assess → [rewrite → retrieve → evaluate]* → generate")

# ============================================================
# 테스트 실행
# ============================================================
test_questions = [
    "LangGraph에서 조건부 분기는 어떻게 구현하나요?",
    "안녕하세요, 오늘 날씨 어때요?",
    "RAG와 에이전트의 차이점을 설명해주세요.",
]

for i, question in enumerate(test_questions, 1):
    print(f"\n{'=' * 60}")
    print(f"테스트 {i}: {question}")
    print("=" * 60)

    result = app.invoke({
        "question": question,
        "rewritten_query": "",
        "documents": [],
        "needs_retrieval": False,
        "is_sufficient": False,
        "answer": "",
        "iteration": 0,
    })

    print(f"\n답변: {result['answer'][:300]}...")
    print(f"검색 수행: {'예' if result['needs_retrieval'] else '아니오'}, 반복: {result['iteration']}회")

# 정리
vectorstore.delete_collection()
print("\n벡터 스토어 정리 완료")

print("\n" + "=" * 60)
print("기존 RAG vs Agentic RAG 비교:")
print("─" * 60)
print("기존 RAG:    질문 → (항상) 검색 → 응답")
print("Agentic RAG: 질문 → 필요성 판단 → 쿼리 최적화 → 검색 → 충분성 평가 → 응답")
print("─" * 60)
print("\n설명:")
print("1. 검색 필요성 판단: 모든 질문에 검색을 수행하지 않고, 필요할 때만 검색합니다.")
print("2. 쿼리 재작성: 사용자 질문을 검색에 최적화된 쿼리로 변환합니다.")
print("3. 충분성 평가: 검색 결과가 부족하면 쿼리를 재작성하여 재검색합니다.")
print("4. 적응적 루프: 에이전트가 검색 전략을 능동적으로 조정합니다.")
