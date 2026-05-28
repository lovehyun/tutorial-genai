"""
Short-term + Long-term 메모리 결합 — 실무 정석 패턴

두 메모리가 같이 일할 때의 구조:
  - **long-term**  : 세션을 가로질러 유지되는 사용자 프로필 (profile.json)
                    → system prompt 에 사실로 주입
  - **short-term** : 현재 세션의 대화 history
                    → MessagesPlaceholder 로 같은 prompt 에 끼움

  long-term  = "당신은 누구인지" 의 영속 사실
  short-term = "지금 대화의 흐름"

5.1 을 한 번 실행해서 profile.json 을 만든 뒤 이 파일을 실행하면,
long-term 으로 사용자를 이미 알고 있는 상태에서 short-term 대화가 이어집니다.
"""

import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

PROFILE_FILE = Path("profile.json")


# ─────────────────────────────────────────────────────────────
# long-term : profile.json 로드 (5.1 이 만들어둠)
# ─────────────────────────────────────────────────────────────
def load_profile() -> dict:
    if PROFILE_FILE.exists():
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    return {}

profile = load_profile()
print(f"[long-term 프로필] {profile or '(비어있음 — 먼저 5.1 을 실행하세요)'}\n")


def system_prompt_with_profile() -> str:
    """long-term 정보를 system 프롬프트의 사실 박스로 주입"""
    if not profile:
        return "당신은 친절한 한국어 어시스턴트입니다."
    facts = ", ".join(f"{k}={v}" for k, v in profile.items())
    return (
        "당신은 친절한 한국어 어시스턴트입니다.\n"
        f"[사용자 영속 정보] {facts}\n"
        "위 정보는 이전 세션들에서 누적된 사실입니다. 신뢰하고 활용하세요."
    )


# ─────────────────────────────────────────────────────────────
# short-term : 현재 세션의 대화 history
# ─────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_with_profile()),    # ← long-term
    MessagesPlaceholder("history"),              # ← short-term
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()
chatbot = RunnableWithMessageHistory(
    chain, lambda _: memory,
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message):
    print(f"\nQ: {message}")
    print(f"A: {chatbot.invoke(
        {'input': message},
        config={'configurable': {'session_id': 'default'}},
    )}")


# ─────────────────────────────────────────────────────────────
# 새 세션 시작 — 사용자가 자기 소개를 안 했는데도 LLM 이 이미 안다.
# (long-term 의 힘)
# ─────────────────────────────────────────────────────────────
chat("나 누군지 알지?")                         # long-term 으로 답함
chat("최근에 한라산 다녀왔어.")                  # short-term 누적
chat("내가 다녀온 곳이 어디고 내 취미가 뭐였지?")  # long-term + short-term 둘 다 사용
