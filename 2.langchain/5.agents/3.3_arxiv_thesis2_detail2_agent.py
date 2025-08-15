# pip install langchain_openai arxiv python-dotenv
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

from langchain.agents import initialize_agent, AgentType
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun


# 0. 환경 변수 로드
load_dotenv()

# 1. ChatOpenAI로 LLM 설정 (gpt-4o-mini 사용)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 검색기 세팅: 최신순, 상위 5건
# arXiv 도구 직접 구성(최신순+상위5)
arxiv = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(
        top_k_results=5,
        load_max_docs=5,
        sort_by="lastUpdatedDate",
        sort_order="descending",
    )
)
tools = [arxiv]

# 3. 시스템 프롬프스 설정
system_prompt = """\
당신은 Structured Chat Agent입니다. 다음을 반드시 지키세요.
1) arXiv 도구는 정확히 '한 번만' 호출합니다.
2) 질의는 다음과 같이 구체적으로 생성합니다:
   - 주제 키워드(예: "deep learning")
   - 보조 키워드(예: "survey", "overview", "foundation model")
   - 불필요한 중복/재시도 금지
3) 응답 형식:
   - 각 논문: 제목 / 저자 / 연도 / 핵심 기여 / 한계(있으면)
   - 마지막에 최근 경향 3줄 정리
4) 한국어로만 답변합니다.
"""

# 4. 에이전트 설정
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": SystemMessage(content=system_prompt)},
    max_iterations=5,                 # 반복 억제
    early_stopping_method="generate", # 중간 실패 시 생성으로 종료
    handle_parsing_errors=True,       # 파싱 에러 스킵
    verbose=True,
)

# max_iterations=5 — 에이전트의 최대 반복 횟수 제한
# - 에이전트는 내부적으로 "생각(Thought) → 도구 실행(Action) → 관찰(Observation)" 단계를 반복합니다.
# - 기본값은 15회 정도라, 질의가 광범위하거나 툴 응답이 만족스럽지 않으면 계속 재시도 루프에 빠질 수 있습니다.
# - max_iterations=5로 지정하면, 최대 5번만 툴 호출/응답 사이클을 돌리고, 그 안에 해결 못 하면 중단합니다.
# - 장점: 무한 루프 방지, 실행 시간 단축
# - 단점: 너무 낮게 잡으면, 복잡한 질의에서 결과를 못 얻고 중간에 종료될 수 있음

# early_stopping_method="generate" - 중간 실패 시 강제 생성 모드로 종료
# - 에이전트가 max_iterations에 도달했거나, 더 이상 진행 방법을 못 찾을 때 동작 방식을 지정합니다.
# - "generate" 모드:
#   - 지금까지 얻은 정보를 바탕으로 LLM이 바로 최종 답변을 생성합니다.
#   - 즉, "더 이상 도구 실행 안 하고, 지금 있는 정보로 마무리하자" 는 의미입니다.
# - "force" 모드:
#   - 단순히 중단하고, 실패를 의미하는 메시지 반환 (기본적으로 "Agent stopped due to iteration limit or time limit.")
# - "generate"는 결과가 비어 있거나 미완성이어도, 사용자가 볼 수 있는 최대한 완성된 답변을 만들어줍니다.

# handle_parsing_errors=True - 파싱 에러 무시하고 계속 진행
# - 에이전트는 툴 호출 시 JSON 형식의 명령문을 내부적으로 파싱합니다.
# - 하지만 LLM 출력이 예상 형식과 다르면 파싱 에러가 발생합니다.
# - True로 설정하면:
#   - 파싱에 실패해도 프로그램이 즉시 중단되지 않고,
#   - 해당 단계는 건너뛰거나 LLM에 "형식을 고쳐라" 요청 후 계속 진행합니다.
# - 기본값은 False → 형식이 틀리면 바로 예외 발생
# - 장점: 실행 도중 발생하는 사소한 출력 형식 문제를 완화
# - 단점: 잘못된 형식이 계속 반복되면, 의도와 다른 행동을 할 수 있음


# 5. 사용자 요청 
user_prompt = "최근 딥러닝 논문 동향을 찾아 간단히 요약해줘. (survey/overview 위주)"
result = agent.invoke({"input": user_prompt})
print(result.get("output", result))
