"""
미들웨어 (1) — SummarizationMiddleware 로 긴 대화 자동 요약 (컨텍스트 관리).
이 예제: 대화가 길어지면 오래된 메시지를 '요약'으로 압축해 토큰 폭발을 막는다.

trim(5.5) vs summarize(여기):
  - trim     : 오래된 메시지를 '버림'        (정보 손실, 빠름, LLM 호출 없음)
  - summarize: 오래된 메시지를 '요약으로 압축' (핵심 보존, 요약용 LLM 호출 추가)

미들웨어란?
  - create_agent(middleware=[...]) 로 끼우는 '플러그인' — 모델/도구 호출 전후에 개입
  - langchain 1.x 의 표준 확장 방식 (요약/HITL/가드레일/재시도 등이 모두 미들웨어)
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    llm,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=llm,
            trigger=("messages", 6),   # 메시지가 6개를 넘으면 요약 발동
            keep=("messages", 2),      # 최근 2개는 원문 그대로 유지
        )
    ],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "t1"}}
turns = [
    "내 이름은 앨리스야.",
    "나는 서울에 살아.",
    "취미는 등산이야.",
    "어제 북한산에 다녀왔어.",
    "다음엔 설악산에 가고 싶어.",
    "그런데 내 이름이 뭐였지?",   # 오래된 메시지가 요약됐어도 이름은 기억해야 함
]
for t in turns:
    result = agent.invoke({"messages": [("user", t)]}, config=config)
    print(f"Q: {t}\nA: {result['messages'][-1].content}\n")

state = agent.get_state(config)
print(f"현재 상태 메시지 수: {len(state.values['messages'])}  (요약 압축으로 무한정 늘지 않음)")


# 정리:
#   - SummarizationMiddleware(model, trigger=..., keep=...) 한 줄로 자동 요약
#   - trigger=('messages', N) / ('tokens', N) / ('fraction', 0.8)
#   - keep=('messages', N) → 최근 N개는 원문 유지, 나머지는 요약으로 대체
#   - 단순히 '버리는' 방식은 5.5_trim_messages
