# pip install arxiv
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
# from langchain_community.agent_toolkits.load_tools import load_tools
# from langchain.agents import initialize_agent, AgentType

from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun

# 0. 환경 변수 로드
load_dotenv()

# 1. ChatOpenAI로 LLM 설정 (gpt-4o-mini 사용)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# 2. arXiv 도구 로드 (API 키 필요 없음)
# tools = load_tools(["arxiv"])

# 2. 검색기 세팅: 최신순, 상위 5건
arxiv = ArxivAPIWrapper(
    top_k_results=5,
    load_max_docs=5,               # 문서 로딩 상한
    sort_by="lastUpdatedDate",     # 최신 업데이트순
    sort_order="descending",
)

# 도구 직접 실행(에이전트 미사용)
tool = ArxivQueryRun(api_wrapper=arxiv)


# 3. 질의는 구체화: 주제+기간/키워드
query = 'deep learning AND (survey OR overview OR foundation model)'

raw = tool.run(query)  # 문자열(메타+초록 요약)로 반환

# 4. 요약
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
summary_prompt = f"""
아래 arXiv 검색 결과를 한국어로 요약해 주세요.
- 논문 5건 내외, 각 논문: 제목 / 저자 / 연도 / 핵심 기여 / 한계(있으면)
- 마지막에 '최근 경향' 3줄 정리

[검색결과]
{raw}
"""

result = llm.invoke(summary_prompt)
print(result.content)
