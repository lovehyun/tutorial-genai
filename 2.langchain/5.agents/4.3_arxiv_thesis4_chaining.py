from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence

# 환경 변수 로드
load_dotenv()

# 요약용 LLM
llm_summary = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 번역용 LLM
llm_translate = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# arXiv 툴 로드
tools = load_tools(["arxiv"])

# 1단계: 에이전트 (논문 검색 + 요약)
agent = initialize_agent(
    tools=tools,
    llm=llm_summary,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 2단계: 번역 체인 프롬프트
translate_prompt = ChatPromptTemplate.from_template(
    "다음을 한국어로 자연스럽게 번역해줘:\n\n{text}"
)
translation_chain = translate_prompt | llm_translate | RunnableLambda(lambda x: x.content.strip())

# 전체 체인 구성 (agent → 번역)
full_chain = (
    RunnableLambda(lambda input: {"input": input["query"]})  # 입력값 포맷 맞추기
    | RunnableLambda(agent.invoke)                           # 요약 실행
    | (lambda x: {"text": x["output"]})                      # 요약 출력 → 번역 입력으로 포맷 변경
    | translation_chain                                      # 번역 실행
)

# 체인을 하나로 통합
# full_chain = (
#     RunnableLambda(lambda x: {"input": x["query"]})  # 사용자 쿼리 → agent 입력 포맷
#     | RunnableLambda(agent.invoke)                   # agent 실행 → {"output": ...}
#     | RunnableLambda(lambda x: {"text": x["output"]})  # 번역용 입력 포맷
#     | (ChatPromptTemplate.from_template("다음을 한국어로 자연스럽게 번역해줘:\n\n{text}")
#     | ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
#     | RunnableLambda(lambda x: x.content.strip()))
# )

# 실행
result = full_chain.invoke({"query": "최근의 딥러닝 관련 논문을 찾아서 요약해줘"})

# 출력
print("\n번역된 요약 결과:\n", result)
