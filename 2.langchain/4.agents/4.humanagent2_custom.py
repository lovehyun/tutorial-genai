from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

# 커스텀 human 툴 정의
def custom_human_input(prompt):
    print(f"\n사용자에게 질문합니다: {prompt}")
    return input("당신의 답변을 입력해주세요: ")

# 커스텀 툴 생성
human_tool = Tool(
    name="Human Input",
    func=custom_human_input,
    description="사용자에게 추가 정보가 필요할 때 사용합니다. 질문할 내용을 입력하세요."
)

# 에이전트 초기화
agent_chain = initialize_agent(
    tools=[human_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 모델 실행
result = agent_chain.invoke({"input": "What's my nickname?"})
print("\n최종 결과:", result["output"])
