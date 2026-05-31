"""
Agentic RAG (1) 기본 — 에이전트가 '검색할지 말지' 스스로 결정.
이 예제: 모든 질문에 무조건 검색하지 않고, LLM 이 먼저 "이 질문에 검색이 필요한가?"
를 판단해 필요할 때만 검색합니다. (LangGraph 없이 평범한 if 분기로)

기존 RAG:      질문 → (무조건) 검색 → 응답
Agentic (기본): 질문 → [검색 필요?] → 필요하면 검색 후 응답 / 아니면 곧장 응답

  · 다음 단계(6.2): 쿼리 재작성 + 결과 충분성 평가 + 재시도 루프 추가
  · 그 다음(6.3) : 똑같은 로직을 LangGraph 그래프로 재구성
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

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


# ─── 에이전트의 '판단' — 검색이 필요한 질문인가? ──────
def needs_retrieval(question: str) -> bool:
    resp = llm.invoke([
        SystemMessage(content="질문이 외부 문서 검색이 필요하면 YES, 아니면(인사/일반대화/계산 등) NO. 한 단어만."),
        HumanMessage(content=question),
    ])
    decision = "YES" in resp.content.upper()
    print(f"  [판단] 검색 필요: {'예' if decision else '아니오'}")
    return decision


# ─── 답변 — 판단 결과에 따라 분기 ─────────────────────
def answer(question: str) -> str:
    if needs_retrieval(question):
        docs = retriever.invoke(question)
        print(f"  [검색] {len(docs)} 개 문서")
        context = "\n".join(d.page_content for d in docs)
        prompt = f"자료만 보고 답하세요. 자료에 없으면 추측 금지.\n\n자료:\n{context}\n\n질문: {question}"
    else:
        prompt = question   # 검색 없이 곧장 답
    return llm.invoke([HumanMessage(content=prompt)]).content


# ─── 실행 — 검색이 필요한 질문 vs 필요 없는 질문 ──────
for question in [
    "LangGraph 는 어디에 쓰는 거야?",   # 검색 필요
    "안녕하세요!",                       # 검색 불필요
]:
    print(f"\n=== Q: {question} ===")
    print(f"A: {answer(question)[:200]}...")

store.delete_collection()
