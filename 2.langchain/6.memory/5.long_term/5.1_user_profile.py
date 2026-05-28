"""
사용자 프로필 추출 — long-term memory 의 가장 기본 패턴

short-term (history) 는 세션 종료 시 사라집니다.
하지만 "사용자는 이름이 김철수고 등산이 취미" 같은 사실은 다음 세션에서도 알아야 합니다.

이 예제:
  1. 한 세션이 끝나면 LLM 으로 대화에서 사용자 정보를 추출 → profile.json 저장
  2. 다음 실행 시 profile.json 을 로드해 system prompt 에 주입
     → 새 세션에서도 LLM 이 이미 사용자를 아는 상태로 시작

스크립트를 2 번 실행해보세요. 두 번째 실행은 처음 turn 부터 프로필을 기억합니다.
"""

import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

PROFILE_FILE = Path("profile.json")


def load_profile() -> dict:
    if PROFILE_FILE.exists():
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    return {}


def save_profile(profile: dict):
    PROFILE_FILE.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# 1) 시작 시 프로필 로드
profile = load_profile()
print(f"[기존 프로필] {profile or '(비어있음)'}\n")


# 2) 프로필을 system prompt 에 주입
def build_system_prompt() -> str:
    if not profile:
        return "당신은 친절한 한국어 어시스턴트입니다."
    facts = ", ".join(f"{k}={v}" for k, v in profile.items())
    return (
        "당신은 친절한 한국어 어시스턴트입니다. "
        f"사용자에 대해 알고 있는 사실: {facts}"
    )


prompt = ChatPromptTemplate.from_messages([
    ("system", build_system_prompt()),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()
chatbot = RunnableWithMessageHistory(
    chain, lambda _: memory,
    input_messages_key="input",
    history_messages_key="history",
)


# 3) 대화에서 사용자 정보 추출하는 체인
extract_chain = (
    ChatPromptTemplate.from_messages([
        ("system",
         "다음 대화에서 사용자의 개인 정보(이름·나이·직업·취미·거주지 등) 만 JSON 으로 추출하세요. "
         "정보가 없으면 {{}} 반환. 다른 텍스트 없이 JSON 만."),
        ("user", "대화:\n{dialogue}"),
    ])
    | llm | JsonOutputParser()
)


def chat(message):
    print(f"\nQ: {message}")
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}},
    )
    print(f"A: {answer}")


# 4) 한 세션 진행
chat("안녕! 내 이름은 김철수야.")
chat("나는 35살이고 등산이 취미야.")
chat("직업은 백엔드 개발자야.")
chat("내 정보 다 기억하지?")


# 5) 세션 종료 — 프로필 추출 + 저장
dialogue = "\n".join(f"{m.type.upper()}: {m.content}" for m in memory.messages)
new_info = extract_chain.invoke({"dialogue": dialogue})

profile.update(new_info)   # 기존 프로필에 새 정보 병합
save_profile(profile)

print(f"\n[업데이트된 프로필 → {PROFILE_FILE}]")
print(json.dumps(profile, ensure_ascii=False, indent=2))
print("\n→ 다시 실행해보세요. 두 번째 실행은 처음부터 프로필을 알고 시작합니다.")
