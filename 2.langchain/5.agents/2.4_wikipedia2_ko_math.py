# https://python.langchain.com/docs/modules/agents/

# 필요한 패키지 설치 (최신 업데이트 적용)
# pip install langchain_openai wikipedia llm-math numexpr

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.2)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# 2. 툴 로드
# tools = load_tools(["wikipedia", "llm-math"], llm=llm)

# Wikipedia(ko) 도구 직접 생성(언어/검색 옵션 제어)
wiki = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        lang="ko",
        top_k_results=5,
        doc_content_chars_max=4000,
    )
)
tools = [wiki] + load_tools(["llm-math"], llm=llm)

# 3. 시스템 프롬프트 설정

# system_prompt = """\
# You are an AI assistant that must:
# 1. Always use the Wikipedia tool for retrieving factual date information.
# 2. Always use the llm-math tool for arithmetic.
# 3. Present the final result in a table with columns: Holiday, Date, M+D, Cumulative Sum.
# 4. Respond in Korean.
# """

# 계산 정확성 중요 → "모든 계산은 반드시 calculator tool을 사용"
# 형식 고정 → "반드시 JSON으로 응답"
# 언어 고정 → "모든 응답은 한국어로 작성"

system_prompt = """\
당신은 도구를 활용해 신뢰할 수 있는 정보를 수집하고 정확히 계산하는 한국어 비서입니다.
반드시 다음을 지키세요.

1) 사실/날짜 조회는 Wikipedia 도구를 사용하세요.
2) 모든 산술 계산은 llm-math(계산기) 도구를 사용하세요. 임의로 머리로 계산하지 마세요.
3) 출력 형식:
   - '휴일명 | 날짜(M/D) | M+D' 표 형식으로 각 항목을 나열
   - 마지막에 '총합: <숫자>' 한 줄로 결과 제시
4) 가능한 한 출처 텍스트(위키 요약)에서 날짜를 추출하고, 추론으로 지어내지 마세요.
5) 한국어로만 답변하세요.
"""

# 4. LangChain 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={
        "system_message": SystemMessage(content=system_prompt)
    },
    max_iterations=20,
    verbose=True
)

# 5. 사용자 프롬프트 설정

# prompt = """\
# 1. Find the list of public holidays in South Korea with their specific dates (month and day).
# 2. For each holiday, add the month number and day number. For example, for January 1st, add 1 + 1 = 2.
# 3. Then sum all these values to get a final result.
# Please list each calculation step clearly.
# """

prompt = (
    "대한민국의 공휴일 날짜들을 알려주세요. "
    "그리고 각 공휴일의 월과 일을 숫자로 더한 값(M+D)을 계산하고, "
    "마지막에 모든 M+D의 총합을 출력해주세요. 각 계산 과정을 표로 보여주세요."
)

# 6. 모델 실행
result = agent.invoke({"input": prompt})
print(result)
