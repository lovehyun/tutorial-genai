"""
1b와 1d 사이에 끼는 파일 — 1d가 create_agent 로 자동으로 돌리는 걸 여기선 create_agent 없이
손으로 그대로 짠다. "판단 → 실행 → 결과를 LLM에 다시 넣기 → 최종 답변" 을 한 단계씩 눈으로 본다.

순서상으로는 1c 자리(1b 다음)가 맞지만, 정답이 정해진 TODO가 아니라 **강사 전용으로 같이
안 짚고 넘어가도 되는 내용**이라 "c"에 보너스 표시 x 를 붙여 1cx 로 이름 붙였다 — 원래 1c였던
create_agent 버전은 1d 로 밀렸다.

이게 바로 create_agent 가 내부에서 하는 일이다 — create_agent는 이 반복문을
"당신 대신 돌려주는" 라이브러리일 뿐, 새로운 개념이 아니다.

원본: 2.langchain/8.agents/4.internals/4.1_bind_tools.py — 도구만 이 커리큘럼 것(get_word_length
등 3개)으로 바꿨을 뿐, bind_tools→실행→ToolMessage→재호출 흐름은 그 파일과 사실상 동일하다.
(`4.internals`라는 이름 때문에 "고급 부가기능" 폴더처럼 보이지만, 실제로는 2.custom_tools에서
배운 create_agent 의 내부 동작을 나중에 까발리는 자리다.)

── 이거 RAG랑 같은 로직 아닌가? — 맞다 ──────────────────────────
  RAG:        질문 → (항상) 검색 → 검색결과를 프롬프트에 넣기 → LLM이 그 근거로 답변
  이 파일:     질문 → LLM이 "검색할지 말지, 뭘 부를지" 판단 → 실행 → 결과를 메시지에 넣기 → LLM이 그 근거로 답변

  구조가 똑같다 — "외부에서 가져온 정보를 컨텍스트에 넣고 그걸 근거로 답변 생성"이 공통 뼈대다.
  차이는 딱 하나: RAG는 검색이 "무조건 매번 실행되는 고정 단계"이고, 여기(도구 호출)는
  "LLM이 필요한지 스스로 판단해서, 필요한 도구를(검색이든 계산이든 뭐든) 골라 부르는" 것.

  그래서 "Agentic RAG"라는 말이 나온다 — RAG의 검색 단계를 "고정 실행"이 아니라
  "LLM이 고르는 도구 중 하나"로 바꾼 것뿐이다. 이 파일의 get_word_length/calculate_tip/
  lookup_user 자리에 "search_docs(query)" 같은 검색 도구를 넣으면 그게 바로 Agentic RAG의
  뼈대다. → 2.intermediate/1.rag_masterclass 의 Agentic RAG 파트 참고.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


@tool
def get_word_length(word: str) -> int:
    """단어의 글자 수를 센다."""
    return len(word)


@tool
def calculate_tip(amount: float, percent: float) -> float:
    """음식점 영수증 금액과 팁 비율(%) 을 받아 팁 금액을 계산한다.

    Args:
        amount: 음식 가격 (원)
        percent: 팁 비율 (예: 15.0 = 15%)
    """
    return amount * percent / 100


@tool
def lookup_user(user_id: str) -> dict:
    """사용자 ID 로 사용자 정보를 조회한다. 존재하지 않으면 빈 dict 반환."""
    db = {
        "u001": {"name": "홍길동", "city": "서울", "age": 30},
        "u002": {"name": "김철수", "city": "부산", "age": 28},
    }
    return db.get(user_id, {})


tools = [get_word_length, calculate_tip, lookup_user]
name2tool = {t.name: t for t in tools}  # 도구 이름 → 실제 실행할 함수

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)   # 1b와 완전히 같은 시작점


def run_manually(question: str):
    print(f"\n[질문] {question}")
    messages = [HumanMessage(question)]

    # ─── 1) LLM 판단 — 1b에서 이미 본 그 자리 ──────────────────
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        # 도구가 필요 없다고 판단하면 그대로 최종 답변
        print(f"[답변] {response.content}")
        return

    # ─── 2) 실제로 도구를 실행 (1b는 여기서 멈췄었다) ──────────
    for call in response.tool_calls:
        print(f"  → 도구 호출: {call['name']}({call['args']})")
        result = name2tool[call["name"]].invoke(call["args"])
        print(f"  ← 도구 결과: {result}")

        # ─── 3) 결과를 "이 도구 호출에 대한 응답"으로 메시지에 추가 ─
        #   tool_call_id 로 어떤 호출의 결과인지 짝을 맞춰야 한다.
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    # ─── 4) 도구 결과까지 포함해서 LLM을 다시 호출 → 최종 답변 ──
    final_response = llm_with_tools.invoke(messages)
    print(f"[답변] {final_response.content}")


queries = [
    "'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?",
    "5만원 영수증에 15% 팁 얼마야?",
    "u001 사용자 정보 알려줘.",
]

for q in queries:
    run_manually(q)


# ─── 실행 결과 (2026-08-12, gpt-4o-mini) ──────────────────────
# [질문] 'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?
#   → 도구 호출: get_word_length({'word': 'pneumonoultramicroscopicsilicovolcanoconiosis'})
#   ← 도구 결과: 45
# [답변] 'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수는 45개입니다.
#
# [질문] 5만원 영수증에 15% 팁 얼마야?
#   → 도구 호출: calculate_tip({'amount': 50000, 'percent': 15})
#   ← 도구 결과: 7500.0
# [답변] 5만원 영수증에 15% 팁은 7,500원입니다.
#
# [질문] u001 사용자 정보 알려줘.
#   → 도구 호출: lookup_user({'user_id': 'u001'})
#   ← 도구 결과: {'name': '홍길동', 'city': '서울', 'age': 30}
# [답변] 사용자 ID "u001"의 정보는 다음과 같습니다: 이름 홍길동, 도시 서울, 나이 30세.
#
# → 1d(create_agent)와 결과가 사실상 동일하다. 당연하다 — create_agent는 바로 이 반복문을
#   자동으로 돌려주는 것뿐이니까.
