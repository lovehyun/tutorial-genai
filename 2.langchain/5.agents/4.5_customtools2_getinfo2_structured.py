from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage

from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool

import json


# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 사용자 정의 도구 생성 (항상 JSON 문자열로 반환 (ok/value/reason 구조))
@tool
def get_current_weather(location: str) -> str:
    """특정 위치의 현재 날씨 정보를 가져옵니다. '한글' 도시명만 지원합니다. JSON 문자열을 반환합니다."""
    # 실제로는 날씨 API를 호출해야 하지만, 예시이므로 가상 데이터 반환
    weather_data = {
        "서울": "맑음, 기온 22도",
        "부산": "흐림, 기온 25도",
        "제주": "비, 기온 20도"
    }
    
    if location in weather_data:
        # return json.dumps({"ok": True, "value": weather_data[location]})
        return json.dumps({"ok": True, "value": weather_data[location]}, ensure_ascii=False)
    else:
        # return json.dumps({"ok": False, "value": None, "reason": f"'{location}'의 날씨 정보 없음"})
        return json.dumps({"ok": False, "value": None, "reason": f"'{location}'의 날씨 정보 없음"}, ensure_ascii=False)

@tool
def get_population(city: str) -> str:
    """특정 도시의 인구 정보를 가져옵니다. '한글' 도시명만 지원합니다. JSON 문자열을 반환합니다."""
    # 가상 데이터
    population_data = {
        "서울": "약 970만 명",
        "부산": "약 340만 명",
        "인천": "약 300만 명",
        "대구": "약 240만 명"
    }
    
    if city in population_data:
        # return json.dumps({"ok": True, "value": population_data[city]})
        return json.dumps({"ok": True, "value": population_data[city]}, ensure_ascii=False)
    else:
        # return json.dumps({"ok": False, "value": None, "reason": f"'{city}'의 인구 정보 없음"})
        return json.dumps({"ok": False, "value": None, "reason": f"'{city}'의 인구 정보 없음"}, ensure_ascii=False)

# 도구 목록 생성
tools = [get_current_weather, get_population]


# 3. 시스템 프롬프트: 없음은 반드시 없음이라고 말하기
system_rules = SystemMessage(content=(
    "1. 도시 관련 질문에 답할 때, 반드시 사용 가능한 도구의 결과에만 근거해 답하라. "
    "2. 도구가 값을 주지 않으면 '없음'이라고 명확히 말하고, 추정이나 상식으로 채우지 마라. "
    "3. 최종 응답은 한국어로, 다음 형식을 따른다:\n" # 이렇게 해도 잘 안따름
    " - 날씨: <값 또는 없음(이유)>\n"
    " - 인구: <값 또는 없음(이유)>\n"
))

# 4. 에이전트 생성
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": system_rules},
    handle_parsing_errors=True,
    early_stopping_method="force",   # 생성으로 마무리 금지
    return_intermediate_steps=True,  # 중간 툴 결과를 돌려받음 (result["intermediate_steps"])
    max_iterations=5,
    verbose=True,
)

# 5. 에이전트 실행
# result = agent.invoke({"input": "서울의 날씨는 어때? 그리고 인구는 몇 명이야?"})
result = agent.invoke({"input": "인천의 날씨는 어때? 그리고 인구는 몇 명이야?"})
# result = agent.invoke({"input": "제주의 날씨는 어때? 그리고 인구는 몇 명이야?"})
print(result["output"])


# ReAct/StructuredChat 에이전트는 "툴을 언제·어떻게 쓸지" 는 잘하지만, 출력 형식을 100% 강제하진 못합니다.
# LLM은 \uXXXX 형태의 유니코드 이스케이프 문자열도 정상적으로 이해할 수 있습니다. (그럼에도 디버그 편의상 ensure_ascii=False 추가해서 한글로 출력)


# 6. 출력 포멧팅
def _render_line(label: str, rec: dict | None) -> str:
    if rec and rec.get("ok"):
        return f"- {label}: {rec['value']}"
   
    # 없음/실패 케이스
    reason = (rec or {}).get("reason", "정보 없음")
    return f"- {label}: 없음({reason})"

def ask_city(city: str) -> str:
    """에이전트를 호출하되, 최종 출력은 우리가 고정 포맷으로 렌더링"""
    result = agent.invoke({"input": f"{city}의 날씨는 어때? 그리고 인구는 몇 명이야?"})

    weather_rec, pop_rec = None, None
    
    # 중간 Observation을 파싱 (ensure_ascii=False 덕분에 한글 그대로 들어옴)
    for action, observation in result["intermediate_steps"]:
        # observation은 문자열(JSON). 디버깅 편의: 사람이 읽기 좋게 출력
        try:
            parsed = json.loads(observation)
        except Exception:
            parsed = None
        
        if action.tool == "get_current_weather":
            weather_rec = parsed
            # 사람이 읽기 좋게 로그(선택)
            print("Weather Observation:", json.dumps(parsed, ensure_ascii=False))
        elif action.tool == "get_population":
            pop_rec = parsed
            print("Population Observation:", json.dumps(parsed, ensure_ascii=False))

    # 에이전트의 자유형 최종 답(result["output"])은 무시하고, 우리가 원하는 형식으로 항상 렌더링
    return "\n".join([
        _render_line("날씨", weather_rec),
        _render_line("인구",  pop_rec),
    ])

# 실행 예시
# print(ask_city("인천"))
# 기대 출력:
# - 날씨: 없음('인천'의 날씨 정보 없음)
# - 인구: 약 300만 명
