# pip install claude-agent-sdk anyio
#
# 2단계: 메시지 스트림 이해하기 — query()가 실제로 뭘 흘려보내는지 종류별로 확인한다.
#
# 1.hello_query.py에서는 AssistantMessage/ResultMessage만 골라 썼다. 실제로는 더 많은 타입이 온다:
#   SystemMessage  — 세션 시작 정보 (세션 id, 켜진 도구 목록, cwd 등) — 보통 맨 처음 1번
#   AssistantMessage — 모델의 응답(텍스트/도구호출 블록 포함) — 턴마다 옴
#   ResultMessage  — 이 실행이 끝났다는 신호 + 최종 비용/턴 수/에러 여부 — 보통 마지막 1번
# (환경에 따라 RateLimitEvent 등 다른 이벤트가 더 섞여 올 수도 있다 — else 분기로 확인)

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, SystemMessage, ResultMessage

options = ClaudeAgentOptions(
    tools=[],
    system_prompt="You are a concise assistant.",
    max_turns=1,
    max_budget_usd=0.05,
)


async def main():
    async for message in query(prompt="파이썬과 자바스크립트의 차이를 한 문장으로.", options=options):
        # [관전 포인트] 타입으로 분기해서 각 메시지가 실제로 뭘 담고 있는지 확인한다.
        if isinstance(message, SystemMessage):
            print(f"[SystemMessage] session_id={message.data.get('session_id')}, "
                  f"model={message.data.get('model')}, tools={message.data.get('tools')}")
        elif isinstance(message, AssistantMessage):
            texts = [b.text for b in message.content if hasattr(b, "text")]
            print(f"[AssistantMessage] {' '.join(texts)}")
        elif isinstance(message, ResultMessage):
            print(f"[ResultMessage] 성공={not message.is_error}, "
                  f"비용=${message.total_cost_usd:.4f}, 소요={message.duration_ms}ms")
        else:
            print(f"[{type(message).__name__}] {message}")


anyio.run(main)
