"""
arXiv 빌트인 도구 — 학술 논문 메타데이터 검색.
이 예제: arxiv_search 도구로 논문을 찾고, 결과를 한국어로 자동 요약/번역합니다.

언제 쓰나:
  - "최근 RAG 관련 논문 알려줘" 같은 학술 리서치 질문
  - LLM 지식 cut-off 이후의 신규 논문 찾기

검색은 영어 키워드가 정확도 ↑.

  ※ pip install arxiv
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langgraph.prebuilt import create_react_agent

load_dotenv()


arxiv_tool = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=2500,
        load_max_docs=3,
    ),
    name="arxiv_search",
    description=(
        "arXiv 학술 데이터베이스에서 논문을 검색한다. "
        "딥러닝/AI/물리/수학 등의 학술 주제에 사용. "
        "입력은 영어 키워드가 더 좋은 결과를 낸다."
    ),
)


system_prompt = """\
당신은 학술 논문을 검색하고 한국어로 요약·번역해주는 비서입니다.

작업 흐름:
1) 사용자 질문에서 핵심 키워드 추출 (영어로 번역해 검색 정확도 ↑)
2) arxiv_search 도구로 논문 검색 — **1번만**. 검색어 바꿔서 재시도 금지.
3) 결과를 다음 형식으로 한국어 정리:
   - 제목 (원문 영어 + 한국어 번역)
   - 저자
   - 핵심 요약 (3~4문장, 한국어)
   - arXiv 링크

도구 결과가 비어 있으면 "관련 논문을 찾지 못했습니다" 라고만 답하고 종료.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [arxiv_tool], prompt=system_prompt)


question = "최근 retrieval-augmented generation (RAG) 관련 흥미로운 논문 알려줘."

print("=" * 60)
print(f"[질문] {question}")
print("=" * 60)

result = agent.invoke(
    {"messages": [("user", question)]},
    config={"recursion_limit": 15},
)

for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  → 도구 호출: {c['name']}({c['args']})")
    if m.type == "tool":
        print(f"  ← 검색 결과 (앞부분): {m.content[:200]}...")

print(f"\n[최종 답변]\n{result['messages'][-1].content}")
