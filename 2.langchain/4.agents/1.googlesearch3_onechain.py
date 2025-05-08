from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화 
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
translator = OpenAI(temperature=0.3, max_tokens=1024)  # 번역용 모델

# Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요
tools = load_tools(["google-search"])

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True  # 중간 단계 결과 반환 활성화
)

# 에이전트를 함수로 래핑하여 체인에서 사용할 수 있게 함
def run_agent(query):
    result = agent.invoke({"input": query})
    return result["output"]

agent_runnable = RunnableLambda(run_agent)

# 번역 프롬프트
translate_prompt = PromptTemplate.from_template(
    "Translate the following English text into Korean:\n\n{text}"
)

# 번역 체인
translate_chain = (
    translate_prompt 
    | translator 
    | StrOutputParser()
)

# 전체 파이프라인: 검색 -> 번역
search_and_translate_chain = (
    RunnablePassthrough()
    | agent_runnable 
    | RunnableLambda(lambda result: {"original": result, "text": result})
    | RunnablePassthrough.assign(
        translated=lambda x: translate_chain.invoke(x)
    )
)

# 실행
# user_query = input("검색할 내용을 입력하세요: ")
user_query = "서울의 오늘 날씨는 어때?"
result = search_and_translate_chain.invoke(user_query)

print("\n[검색 결과 (원문)]:\n", result["original"])
print("\n[번역 결과]:\n", result["translated"].strip())
