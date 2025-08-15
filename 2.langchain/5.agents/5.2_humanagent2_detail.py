from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.schema import SystemMessage

load_dotenv()

# 1. 모델 정의
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Human 도구 로드 (stdin 기반)
# tools = load_tools(["human"])

# 동일 기능을 직접 만들려면
from langchain.tools.human.tool import HumanInputRun

# 프롬프트를 직접 출력하고 flush, 그리고 "" 반환
def pretty_prompt(msg: str) -> str:
    print(f"\n[에이전트가 묻습니다]\n{msg}\n> ", end="", flush=True)
    return ""  # input("")로 호출되게

human = HumanInputRun(
    # input()에 들어갈 프롬프트 문자열을 리턴해야 함
    prompt_func=pretty_prompt
    # input_func는 기본 input으로 두면 충분 (특별히 바꿀 필요 없으면 생략 가능)
    # input_func=input,
)

tools = [human]

# 2) “되물음 규칙”을 시스템 메시지로 간단히 주입
sys_rules = SystemMessage(content=
    # "모르는 개인 정보는 'human' 도구로 사람에게 딱 한 번, 짧게 묻고, "
    "모르는 개인 정보는 'human' 도구로 사람에게 답을 할때까지 반복적으로 묻고, "
    "답을 받으면 그걸로 최종 답을 한국어로 간단히 알려라. 추측 금지."
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    # agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # 구조화된 ReAct 권장
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": sys_rules},
    handle_parsing_errors=True,
    max_iterations=3,                 # 질문→답→최종 응답 정도로 제한
    early_stopping_method="force",    # 억지 생성 마무리 금지
    verbose=True
)

# 실행: 터미널에서 에이전트가 사람에게 되묻게 됨
# question = "What's my nickname?"
question = "내 이름은 뭐야?"

result = agent.invoke({"input": question})
print(result["output"])
