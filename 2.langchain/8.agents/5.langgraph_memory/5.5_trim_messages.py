"""
컨텍스트 관리 (1) — trim_messages 로 오래된 메시지 '잘라내기'.
이 예제: 긴 대화에서 최근 N개(또는 토큰 한도)만 남겨 모델에 보낼 메시지를 줄인다.

왜?
  - 멀티턴이 길어지면 매 호출 토큰이 누적되어 비용·지연·컨텍스트 한도 문제
  - 두 가지 전략:  trim(여기) = 오래된 걸 '버림' / summarize(12.1) = '요약으로 압축'
"""

from dotenv import load_dotenv

from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, trim_messages,
)
from langchain_openai import ChatOpenAI

load_dotenv()


# ─── 긴 대화 예시 (메시지 8개) ──────────────────────────────
conversation = [
    SystemMessage("너는 친절한 비서다."),
    HumanMessage("내 이름은 앨리스야."),
    AIMessage("반가워요, 앨리스!"),
    HumanMessage("나는 서울에 살아."),
    AIMessage("서울 좋죠!"),
    HumanMessage("취미는 등산이야."),
    AIMessage("멋진 취미네요."),
    HumanMessage("방금 내가 뭐라고 했지?"),
]
print(f"원본 메시지 수: {len(conversation)}")


# ─── 전략 1: 최근 '메시지 수' 기준 (system 유지) ────────────
# token_counter=len → '메시지 1개 = 1토큰'으로 세어 개수 제한처럼 사용
trimmed_count = trim_messages(
    conversation,
    max_tokens=4,                # 최근 4개만
    strategy="last",             # 뒤(최근)에서부터 유지
    token_counter=len,
    include_system=True,         # system 메시지는 보존
    start_on="human",            # human 메시지부터 시작하도록 정렬
)
print(f"\n[전략1] 최근 4개 + system 유지 → {len(trimmed_count)}개")
for m in trimmed_count:
    print(f"   {m.type:7} {m.content}")


# ─── 전략 2: '토큰 한도' 기준 (실제 토큰 계산) ──────────────
llm = ChatOpenAI(model="gpt-4o-mini")
trimmed_tokens = trim_messages(
    conversation,
    max_tokens=30,               # 30 토큰 이내
    strategy="last",
    token_counter=llm,           # 모델의 실제 토크나이저로 계산
    include_system=True,
    start_on="human",
)
print(f"\n[전략2] 30토큰 이내 + system 유지 → {len(trimmed_tokens)}개")
for m in trimmed_tokens:
    print(f"   {m.type:7} {m.content}")


# 정리:
#   - trim_messages(msgs, max_tokens=, strategy='last', token_counter=, include_system=)
#   - token_counter=len → 메시지 개수 / token_counter=llm → 실제 토큰
#   - 에이전트에 적용하려면 before_model 미들웨어에서 trim (12.3) 또는 요약(12.1)
#   - 정보 손실이 싫으면 '버리기' 대신 '요약' → 12.1_summarization
