from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage

from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool


# "빌트인 HumanInputRun" 대신 직접 만든 Human 툴을 써서 프롬프트/입력 UX를 100% 내 마음대로 제어
# 뭐가 다른가?
# - 이전(빌트인 HumanInputRun): prompt_func/input_func로 커스터마이즈는 가능하지만, 내부 동작/표시는 제한적.
# - 지금(직접 Tool 정의): print 형식, 다국어 안내, 검증 로직, 로깅, 마스킹, 추가 질문 흐름 등 모든 UX를 직접 설계 가능.


# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2-1. 커스텀 human 툴 정의

# def custom_human_input(prompt):
#     print(f"\n사용자에게 질문합니다: {prompt}")
#     return input("당신의 답변을 입력해주세요: ")

def custom_human_input(prompt: str) -> str:
    # 보기 좋게 출력 + 즉시 flush
    print(f"\n[에이전트가 묻습니다]\n{prompt}\n> ", end="", flush=True)
    ans = input()
    # 예: 공백 정리/간단 검증/마스킹
    ans = ans.strip()
    # 필요하면: ans = re.sub(r'\S', '*', ans)  # 마스킹 예
    return ans


# 2-2. 커스텀 툴 생성
human_tool = Tool(
    name="Human Input",
    func=custom_human_input,
    description="사용자에게 한 줄 질문을 던지고 응답을 받는다. 질문은 짧고 구체적으로 작성할 것."
)

# Tool로 직접 Human 툴을 "직접 정의" 합니다. 
# 프롬프트/입력 방식/검증/로그/비동기/웹 UI 연동 등 모든 걸 원하는 대로 제어할 수 있습니다.


# 3. 에이전트 초기화
agent_chain = initialize_agent(
    tools=[human_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# rules = SystemMessage(content=
#     "모르는 개인 정보는 Human Input 도구로 '단 한 번' 짧게 물어봐라. "
#     "답을 받으면 한국어로 간단히 최종 답을 말하라. 추측/지어내기 금지."
# )

# agent = initialize_agent(
#     tools=[human_tool],
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     agent_kwargs={"system_message": rules},
#     handle_parsing_errors=True,
#     max_iterations=3,
#     early_stopping_method="force",
#     verbose=True
# )


# 4. 모델 실행
# result = agent_chain.invoke({"input": "What's my nickname?"})
result = agent_chain.invoke({"input": "내 이름은 뭐야?"})
print("\n최종 결과:", result["output"])
