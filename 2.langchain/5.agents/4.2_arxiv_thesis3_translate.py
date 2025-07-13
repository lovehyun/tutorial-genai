# pip install arxiv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드
load_dotenv()

# 1. 논문 검색 + 요약을 위한 LLM (gpt-4o-mini)
llm_summary = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 번역을 위한 별도 LLM (같은 모델로도 가능, 설정 달리할 수도 있음)
llm_translate = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# 3. arXiv 도구 로드
tools = load_tools(["arxiv"])

# 4. 에이전트 초기화 (요약 전담)
agent = initialize_agent(
    tools=tools,
    llm=llm_summary,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 5. 번역 체인 구성
translate_prompt = ChatPromptTemplate.from_template(
    "다음을 한국어로 자연스럽게 번역해줘:\n\n{text}"
)
translation_chain = translate_prompt | llm_translate | RunnableLambda(lambda x: {"translated": x.content.strip()})

# 6. 논문 요약 실행
search_result = agent.invoke({"input": "최근의 딥러닝 관련 논문을 찾아서 요약해줘"})

# 7. 번역 실행
translated_result = translation_chain.invoke({"text": search_result["output"]})

# 8. 출력
print("\n요약:\n", search_result["output"])
print("\n번역:\n", translated_result["translated"])
