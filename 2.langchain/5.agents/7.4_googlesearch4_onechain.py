from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화 
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# translator = OpenAI(temperature=0.3, max_tokens=1024)  # 번역용 모델
translator = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=1024)  # 번역용 모델

# 2. Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요
tools = load_tools(["google-search"])

# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True  # 중간 단계 결과 반환 활성화
)

# 4. 번역 프롬프트
translate_prompt = PromptTemplate.from_template(
    "Translate the following English text into Korean:\n\n{text}"
)

# 5-1. 번역 체인
translate_chain = translate_prompt | translator | StrOutputParser()

# 5-2. 전체 파이프라인: 검색(에이전트) → {original, text} 구성 → 번역 추가
search_and_translate_chain = (
    agent 
    | RunnableLambda(lambda d: {"original": d["output"], "text": d["output"]})
    | RunnablePassthrough.assign(translated=translate_chain)
)

# 6. 실행
# user_query = input("검색할 내용을 입력하세요: ")
user_query = "서울의 오늘 날씨는 어때?"
result = search_and_translate_chain.invoke(user_query)

print("\n[검색 결과 (원문)]:\n", result["original"])
print("\n[번역 결과]:\n", result["translated"].strip())
