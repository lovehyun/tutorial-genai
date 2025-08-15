# pip install -U langchain langchain-openai python-dotenv

from dotenv import load_dotenv

from langchain_openai import OpenAI  # instruct 계열 (원하시면 ChatOpenAI로 교체 가능)
from langchain_openai import ChatOpenAI

from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool

load_dotenv()

# =========================
# 1) "모의 검색" 파서 함수 (하드코딩)
# =========================
def search_google(query: str, max_results: int = 5) -> str:
    """구글 검색을 했다고 가정하고, 상위 결과 예시(하드코딩) 반환"""
    mock = [
        "LangChain 0.3: New Runnable features - https://example.com/langchain-0-3-runnable",
        "OpenAI API updates: function calling v2 - https://example.com/openai-fc-v2",
        "LangChain + OpenAI best practices (2025) - https://example.com/lc-oa-best-practices",
        "LCEL (LangChain Expression Language) tips - https://example.com/lcel-tips",
        "Migrating to langchain_openai SDK - https://example.com/migrate-langchain-openai",
    ]
    return "\n".join(mock[:max_results])

def search_naver(query: str, max_results: int = 5) -> str:
    """네이버 검색을 했다고 가정하고, 상위 결과 예시(하드코딩) 반환"""
    mock = [
        "LangChain 0.3 주요 변경사항 총정리 - https://naver.example.com/langchain-0-3",
        "OpenAI 함수호출 v2 가이드 - https://naver.example.com/openai-fc-v2",
        "LangChain-OpenAI 통합 베스트 프랙티스 - https://naver.example.com/lc-oa-best",
        "LCEL 문법과 체인 최적화 - https://naver.example.com/lcel",
        "langchain_openai 마이그레이션 체크리스트 - https://naver.example.com/migrate",
    ]
    return "\n".join(mock[:max_results])

# =========================
# 2) Human 툴 (엔진 선택)
# =========================
def ask_engine(prompt: str) -> str:
    print(f"\n[에이전트 질문] {prompt}")
    while True:
        choice = input("검색 엔진을 선택하세요 (네이버/구글): ").strip()
        if choice in ("네이버", "구글"):
            return choice
        print("'네이버' 또는 '구글'만 입력해주세요.")

human_tool = Tool(
    name="Human Input",
    func=ask_engine,
    description="사용자에게 네이버/구글 중 어떤 엔진으로 검색할지 물어볼 때 사용합니다."
)

google_tool = Tool(
    name="GoogleSearch",
    func=search_google,
    description="구글에서 질의어를 검색해 상위 결과를 반환합니다(모의 결과). 입력은 '검색어 문자열'입니다."
)

naver_tool = Tool(
    name="NaverSearch",
    func=search_naver,
    description="네이버에서 질의어를 검색해 상위 결과를 반환합니다(모의 결과). 입력은 '검색어 문자열'입니다."
)

# =========================
# 3) LLM & Agent 구성
# =========================
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

agent = initialize_agent(
    tools=[human_tool, google_tool, naver_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# from langchain.schema import SystemMessage

# 시스템 규칙(형식 안정)
# sys_rules = SystemMessage(content=
#     "한국어로 간결히 답하라. 다음 절차를 반드시 따른다:\n"
#     "1) 먼저 HumanInput 도구로 '네이버' 또는 '구글' 중 하나를 딱 한 번 물어본다.\n"
#     "2) 사용자가 선택한 엔진에 해당하는 검색 도구만 호출한다(네이버→NaverSearch, 구글→GoogleSearch).\n"
#     "3) 검색 결과 상위 5개를 목록으로 보여주고, 핵심 요약을 3줄 이내로 작성한다.\n"
#     "4) 추측/지어내기 금지. 규칙 위반 시 중단한다."
# )

# 에이전트
# agent = initialize_agent(
#     tools=[human_tool, google_tool, naver_tool],
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # 구조화 ReAct 권장
#     agent_kwargs={"system_message": sys_rules},
#     handle_parsing_errors=True,
#     max_iterations=4,
#     early_stopping_method="force",
#     verbose=True
# )

# =========================
# 4) 실행 예시
# =========================
task = (
    "다음 검색어를 조회하고 상위 결과 5개를 목록으로 보여준 뒤, 핵심 요약을 3줄 내로 작성하세요. "
    "반드시 먼저 Human Input 도구로 '네이버 또는 구글' 중 하나를 사용자에게 물어본 뒤, "
    "선택된 엔진 전용 Search 도구를 호출하세요. 검색어: 'LangChain OpenAI 최신 변경점'"
)

final = agent.invoke({"input": task})
print("\n[최종 출력]\n", final["output"])
