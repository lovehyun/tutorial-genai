"""
Wikipedia 빌트인 도구 — 사실 기반 답변을 위한 가장 흔한 보조 도구.
이 예제: 한국어 / 영어 위키피디아 두 개를 등록하고, 주제에 맞춰 자동 선택되게 합니다.

왜 위키피디아?
  - LLM 의 지식은 cut-off 가 있고, 사실(특히 인물·날짜) 에 헛소리하기 쉬움
  - 위키피디아 도구로 확인 → "추측 금지, 도구 결과만 사용" 패턴 강제

  ※ pip install wikipedia


─── 자주 만나는 에러: GraphRecursionError ─────────────────────

`wikipedia` 파이썬 패키지는 한국어 / 짧은 쿼리에서 결과가 들쭉날쭉합니다
(disambiguation 페이지, 빈 결과, 인코딩 이슈 등).

프롬프트가 "추측 금지, 도구 결과만 사용" 처럼 너무 빡빡하면 에이전트가
"검색어만 살짝 바꿔서 다시" 를 무한 반복하다 25번 호출에서 GraphRecursionError 발생.

해결책 (이 파일에 모두 적용):
  1) 시스템 프롬프트에 "같은 주제로 2번 이상 검색 금지" 명시
  2) "도구가 도움 안 되면 LLM 지식으로 답하되 출처를 명시" 허용
  3) invoke 시 recursion_limit 명시 (안전장치)
"""

import wikipedia
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.agents import create_agent

load_dotenv()

# Wikipedia 는 2024+ 부터 기본 User-Agent 를 차단 → 일반 브라우저 UA 로 교체해야 동작
# (안 하면 빈 응답이 와서 JSONDecodeError. Wikimedia User-Agent 정책)
wikipedia.wikipedia.USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# ─── 한국어 / 영어 두 도구 등록 ─────────────────────────────
wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko", top_k_results=3, doc_content_chars_max=2000),
    name="wikipedia_ko",
    description="한국어 위키피디아에서 사실/배경 정보를 검색한다. 인물, 사건, 개념 등.",
)

wiki_en = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="en", top_k_results=3, doc_content_chars_max=2000),
    name="wikipedia_en",
    description="English Wikipedia. 글로벌 / 영어권 주제 또는 한국어 위키 정보가 부족할 때 사용.",
)


system_prompt = """\
당신은 위키피디아를 활용해 사실 기반의 답변을 제공하는 한국어 비서입니다.

도구 사용 가이드:
- 한국 관련 주제는 wikipedia_ko, 글로벌/영어권 주제는 wikipedia_en
- **같은 주제로 도구를 2번 이상 호출하지 마세요** (검색어 살짝 바꿔서 재시도하는 것 포함 X)
- 도구 결과가 빈약하거나 disambiguation 형태여도 그 결과만으로 답하고 종료
- 도구가 전혀 도움 안 되면 LLM 자체 지식으로 답하되 "위키 결과 부족 — 일반 지식 기준" 이라고 명시

출력은 한국어, 5문장 이내로 간결히.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [wiki_ko, wiki_en], system_prompt=system_prompt)


for q in ["세종대왕은 누구이고 어떤 업적을 남겼어?",
          "Python 프로그래밍 언어는 누가 만들었어?"]:
    print("\n" + "=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    try:
        result = agent.invoke(
            {"messages": [("user", q)]},
            config={"recursion_limit": 15},   # ← 무한 루프 안전장치
        )
    except Exception as e:
        print(f"  [에러] {type(e).__name__}: {e}")
        continue

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 결과: {m.content[:100]}...")

    print(f"\n[답변] {result['messages'][-1].content}")
