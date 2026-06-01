"""
LangChain 빌트인 도구 카탈로그 — 어떤 도구들이 이미 준비돼 있나? (시작점, 에이전트 X)
이 예제: load_tools 로 즉시 가져올 수 있는 모든 도구 이름을 출력만 합니다 (LLM 호출 없음).

직접 만들기 전에 "이미 누가 만들어둔 게 있나" 확인하는 습관을 들이세요.
이 폴더 (1.builtin_tools) 의 나머지 파일들은 이 중 자주 쓰는 것들을 본격 활용합니다.
  → 다음: 1.1_wikipedia_minimal.py (이 중 wikipedia 를 끼운 가장 단순한 첫 에이전트)

주요 카테고리
  - 무료 / 키 불필요  : wikipedia, arxiv, ddg-search, llm-math
  - 키 필요 (실시간)  : google-serper, tavily, openweathermap-api, bing-search
  - LangChain 내장   : memorize, human (사용자에게 직접 묻기 — legacy)
  - 외부 API 래퍼     : pubmed, stackexchange, reddit_search, news-api 등 다수
"""

from langchain_community.agent_toolkits.load_tools import get_all_tool_names


print("=== load_tools 로 즉시 가져올 수 있는 빌트인 도구들 ===")
names = sorted(get_all_tool_names())
for name in names:
    print(f"  - {name}")

print(f"\n총 {len(names)} 개")

# 이 외에도 langchain_community.tools / langchain_tavily 등 패키지마다 도구가 더 있음.
#   - WikipediaQueryRun, ArxivQueryRun                          → 1.2, 1.7 에서 사용
#   - TavilySearch (langchain-tavily 패키지)                     → 1.5 에서 사용
#   - PythonREPLTool, ShellTool, FileManagementToolkit 등        → 위험하므로 신중히
