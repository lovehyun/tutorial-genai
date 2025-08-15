from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType


# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화 
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    timeout=30,
    max_retries=2,
)

# 2. Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요
tools = load_tools(["google-search"])

# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True  # 개발 중만 True, 운영은 False 권장
)

# 4. 번역 체인 설정
translate_prompt = PromptTemplate.from_template(
    "다음 영어 문장을 자연스러운 한국어로 번역하세요:\n\n{text}"
)

translator_llm = ChatOpenAI(  # 번역은 살짝 온도 올려도 OK
    model="gpt-4o-mini",
    temperature=0.2,
    timeout=30,
    max_retries=2,
)

translate_chain = translate_prompt  | translator_llm | StrOutputParser()

# 5. 검색 및 번역 실행
# user_query = input("검색할 내용을 입력하세요: ")
user_query = "서울의 오늘 날씨는 어때?"

# 5-1. 검색 실행
search_result = agent.invoke({"input": user_query})
print("\n[검색 결과 (원문)]:\n", search_result["output"])

# 5-2. '검색 결과가 영어일 때만' 번역하기 (간단 휴리스틱)
def seems_english(s: str) -> bool:
    # 영문 비중이 높으면 True로 판단 (아주 러프한 판별)
    import re
    letters = re.findall(r"[A-Za-z]", s)
    return len(letters) >= max(1, int(len(s) * 0.3))  # 문장 s에서 영어 알파벳이 차지하는 비율이 30% 이상인지를 판별하는 조건

output_text = search_result["output"]
if seems_english(output_text):
    translated = translate_chain.invoke({"text": output_text})
    print("\n[번역 결과]:\n", translated)
else:
    print("\n[번역 결과]:\n(이미 한국어입니다)")
