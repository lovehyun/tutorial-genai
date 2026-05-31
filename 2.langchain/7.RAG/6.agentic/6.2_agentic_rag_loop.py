"""
Agentic RAG (2) 확장 — 결과가 부족하면 쿼리를 바꿔 다시 검색.
이 예제: 6.1 의 '검색 여부 판단' 에 더해, 쿼리 재작성 + 결과 충분성 평가 + 재시도
루프를 추가합니다. 여전히 LangGraph 없이 평범한 while/for 루프로 흐름을 직접 봅니다.

6.1 → 6.2 추가된 것:
  - rewrite : 질문을 검색용 키워드 쿼리로 재작성 (재시도 시 다른 각도로)
  - evaluate: 검색 결과가 충분한지 LLM 이 평가
  - loop    : 부족하면 최대 2회까지 재작성 → 재검색

  · 다음 단계(6.3): 아래 'if / for / break' 제어 흐름을 그대로 LangGraph 그래프
    (노드 + 조건부 엣지) 로 옮긴 버전입니다. 로직은 같고 표현 방식만 달라집니다.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

MAX_TRIES = 2


# ─── 벡터 스토어 (6.1 과 동일 샘플) ───────────────────
sample_docs = [
    Document(page_content="LangChain 은 LLM 애플리케이션 프레임워크. LCEL 로 체인을 조립한다.", metadata={"src": "langchain"}),
    Document(page_content="RAG 는 외부 문서를 검색해 LLM 응답을 보강하는 기법.", metadata={"src": "rag"}),
    Document(page_content="LangGraph 는 그래프 기반 실행 엔진. 노드와 엣지로 분기/순환 구현.", metadata={"src": "langgraph"}),
    Document(page_content="ChromaDB 는 벡터 DB. 코사인 유사도로 가까운 벡터를 찾는다.", metadata={"src": "chroma"}),
]
splits = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50).split_documents(sample_docs)
store = Chroma.from_documents(splits, embedding=OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="agentic_demo")
retriever = store.as_retriever(search_kwargs={"k": 3})


# ─── 단계별 도우미 함수 ───────────────────────────────
def needs_retrieval(question: str) -> bool:
    resp = llm.invoke([
        SystemMessage(content="질문이 외부 문서 검색이 필요하면 YES, 아니면 NO. 한 단어만."),
        HumanMessage(content=question),
    ])
    decision = "YES" in resp.content.upper()
    print(f"  [판단] 검색 필요: {'예' if decision else '아니오'}")
    return decision


def rewrite_query(question: str, prev_query: str | None, attempt: int) -> str:
    """검색용 쿼리로 재작성. 재시도면 직전 쿼리를 피해 다른 각도로."""
    if prev_query is None:
        prompt = f"다음 질문을 벡터 검색용 키워드 쿼리로 재작성. 쿼리만:\n{question}"
    else:
        prompt = (f"이전 검색이 부족했습니다. 다른 각도로 쿼리 재작성. 쿼리만.\n"
                  f"질문: {question}\n이전 쿼리: {prev_query}")
    query = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    print(f"  [재작성 #{attempt}] {query}")
    return query


def is_sufficient(question: str, docs: list[str]) -> bool:
    resp = llm.invoke([
        SystemMessage(content="검색 결과가 질문에 답하기 충분하면 SUFFICIENT, 아니면 INSUFFICIENT. 한 단어만."),
        HumanMessage(content=f"질문: {question}\n\n결과:\n" + "\n".join(docs)),
    ])
    ok = "SUFFICIENT" in resp.content.upper()
    print(f"  [평가] {'충분' if ok else '부족'}")
    return ok


# ─── 답변 — 평범한 루프로 agentic 흐름 제어 ───────────
def answer(question: str) -> str:
    if not needs_retrieval(question):
        return llm.invoke([HumanMessage(content=question)]).content   # 검색 없이 곧장 답

    query, documents = None, []
    for attempt in range(1, MAX_TRIES + 1):                 # 최대 MAX_TRIES 회
        query = rewrite_query(question, query, attempt)
        documents = [d.page_content for d in retriever.invoke(query)]
        print(f"  [검색] {len(documents)} 개 문서")
        if is_sufficient(question, documents):              # 충분하면 루프 탈출
            break

    context = "\n".join(documents)
    prompt = f"자료만 보고 답하세요. 자료에 없으면 추측 금지.\n\n자료:\n{context}\n\n질문: {question}"
    return llm.invoke([HumanMessage(content=prompt)]).content


# ─── 실행 ─────────────────────────────────────────────
for question in [
    "LangGraph 에서 분기는 어떻게 구현해?",   # 검색 필요 → 재작성/평가 루프
    "2 + 2 는?",                              # 검색 불필요
]:
    print(f"\n=== Q: {question} ===")
    print(f"A: {answer(question)[:200]}...")

store.delete_collection()
