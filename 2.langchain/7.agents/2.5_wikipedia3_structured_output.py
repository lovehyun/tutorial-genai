# 필요한 패키지
# pip install langchain_openai wikipedia llm-math numexpr python-dotenv

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


# 포인트: STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION는 내부적으로 툴 호출을 구조화된 형식으로 유도해, 계산은 계산기로, 검색은 위키로 더 잘 분리되도록 돕습니다.
# 주의할 점
# - 사용하시는 툴이 인자 스키마를 올바르게 노출해야 합니다(커스텀 @tool 사용 시 Pydantic/타입힌트 주의).
# - 모델은 툴 콜링이 가능한 Chat 모델이어야 합니다(ChatOpenAI 4o/4.1/mini 등 OK).
# - verbose=True로 디버깅 로그를 보면서, 툴 선택이 기대대로 되는지 확인해 주세요.


# 0) 환경변수 로드
load_dotenv()

# 1) LLM (툴콜링 지원 모델)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2) 도구 준비
wiki = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        lang="ko",
        top_k_results=5,
        doc_content_chars_max=4000,
    )
)
# llm-math(내부적으로 numexpr 사용) 포함
tools = [wiki] + load_tools(["llm-math"], llm=llm)

# 3) 시스템 프롬프트: JSON만 출력(추가 텍스트/설명 금지)
system_prompt = """\
당신은 Structured Chat Agent입니다. 다음 규칙을 반드시 지키세요.

[행동 규칙]
1) 모든 '사실/날짜' 조회는 Wikipedia 도구만 사용합니다.
2) 모든 산술 계산은 llm-math(계산기) 도구만 사용합니다. 직접 암산/추론 금지.
3) 한국어 공휴일 명칭과 날짜를 한국어로 반환하되, 날짜는 "M/D" 형식(예: "1/1")으로 표기합니다.

[출력 형식(필수 JSON)]
다음 JSON 스키마에 '정확히' 맞춰서 출력하세요. 여분 텍스트/마크다운/설명 금지.

{
  "items": [
    {
      "holiday": "string",          // 공휴일 이름 (예: "신정")
      "date": "M/D",                // 월/일 (예: "1/1")
      "M": number,                  // 월 숫자
      "D": number,                  // 일 숫자
      "M_plus_D": number,           // M + D 값
      "source": "string"            // 위키 문서/요약 등 출처 간단 표기
    }
  ],
  "total_sum": number,              // 모든 M_plus_D의 합
  "notes": "string"                 // 참고(가변 공휴일 처리 등 간단 주석)
}

[검증]
- 항목별 M_plus_D 계산은 반드시 llm-math로 수행하세요.
- 항목 누락/중복을 피하고, 가능한 최신의 '대한민국 공휴일' 목록을 사용하세요.
- JSON 이외의 어떤 텍스트도 출력하지 마세요.
"""

# 4) Structured Chat 에이전트로 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": SystemMessage(content=system_prompt)},
    max_iterations=20,
    verbose=True,
)

# 5) 사용자 요청
user_prompt = (
    "대한민국의 공휴일 목록과 각 날짜(M/D)에 대해 M+D를 수식과 답으로 M+D=Sum 으로 계산해 주세요. "
    "마지막에 모든 M_plus_D의 총합도 JSON 스키마에 맞춰 반환하세요."
)

# 6) 실행
result = agent.invoke({"input": user_prompt})

# 7) 결과(JSON 문자열) 출력
print(result.get("output", result))
