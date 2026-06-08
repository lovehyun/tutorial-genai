"""
에이전틱 RAG — 검색(retriever)을 '도구'로 단 에이전트.
이 예제: 벡터스토어 검색을 @tool 로 감싸 에이전트가 '필요할 때' 스스로 문서를 찾게 한다.

일반 RAG 와의 차이:
  - 고전 RAG : 무조건 '검색 → LLM' 고정 파이프라인 (질문마다 항상 검색)
  - 에이전틱 RAG : LLM 이 '검색이 필요한지' 판단 → 도구 호출 → 필요하면 여러 번/재질의
    (규정과 무관한 질문은 검색 없이 바로 답)
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.agents import create_agent

load_dotenv()


# ─── 1) 작은 지식베이스 → 벡터스토어 ───────────────────────
DOCS = [
    "회사 연차는 입사 1년 후 15일 부여되며, 이후 매년 1일씩 증가한다.",
    "재택근무는 주 3일까지 가능하고, 사전에 팀장 승인이 필요하다.",
    "경조사 휴가는 본인 결혼 5일, 직계가족 사망 5일이다.",
    "사내 카페는 평일 오전 8시부터 오후 6시까지 운영한다.",
]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore.from_texts(DOCS, embedding=embeddings)


# ─── 2) 검색을 '도구'로 ─────────────────────────────────────
@tool
def search_handbook(query: str) -> str:
    """사내 규정 핸드북에서 관련 내용을 검색한다 (연차/재택/휴가/카페 등)."""
    hits = vectorstore.similarity_search(query, k=2)
    return "\n".join(f"- {d.page_content}" for d in hits) or "관련 규정 없음"


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(
    llm,
    [search_handbook],
    system_prompt="사내 규정 질문은 search_handbook 로 근거를 찾아 답하라. "
                  "규정과 무관한 질문은 검색 없이 그냥 답하라.",
)


def run(q: str):
    print(f"\nQ: {q}")
    result = agent.invoke({"messages": [("user", q)]})
    for m in result["messages"]:
        for c in getattr(m, "tool_calls", []) or []:
            print(f"  └─ 검색: {c['args'].get('query')}")
    print(f"A: {result['messages'][-1].content}")


run("연차는 며칠 받을 수 있어?")     # 검색해서 근거 기반 답변
run("2 더하기 3은?")                 # 검색 없이 바로 답


# 정리:
#   - retriever.similarity_search 를 @tool 로 감싸면 = 에이전틱 RAG
#   - LLM 이 검색 여부/횟수를 스스로 판단 (고정 파이프라인 X)
#   - 본격적인 RAG(청킹/리랭킹/평가) → ../../7.RAG/, 검색 도구 여러 개 → 멀티툴(3.1)
