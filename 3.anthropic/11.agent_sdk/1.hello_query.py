# pip install claude-agent-sdk anyio
#
# 1단계: Claude Agent SDK — 가장 단순한 호출.
#
# 지금까지(1.basic ~ 10.langchain)는 `anthropic` SDK로 "질문 → 답변" 한 번을 호출했다.
# Claude Agent SDK는 다르다 — **Claude Code를 구동하는 것과 똑같은 에이전트 루프**를 그대로 코드로 쓴다.
# `2.langchain/8.agents`가 LangChain이라는 프레임워크로 에이전트를 만드는 거라면, 이건
# Anthropic 자체 네이티브 에이전트 프레임워크다(내부적으로 Claude Code CLI를 실행한다).
#
# ⚠️ 중요 — 이건 가벼운 API 호출이 아니다:
#   - 기본값 그대로 두면 Read/Write/Bash 등 Claude Code의 전체 도구 세트가 함께 켜진다.
#   - 시스템 프롬프트도 Claude Code 전체 분량이라 캐시 생성 토큰만 수만 개가 들어간다.
#   - 그래서 이 예제는 tools=[](도구 없음) + 커스텀 system_prompt(짧게) + max_budget_usd(비용 상한)로
#     "그냥 대화만 하는" 가장 얌전한 형태로 켰다. 실전에서는 필요한 도구만 골라 켜야 한다.
#
# 인증: ANTHROPIC_API_KEY가 아니라 **이 컴퓨터에 로그인된 Claude Code CLI 인증**을 그대로 쓴다
#       (미리 `claude` CLI가 설치·로그인돼 있어야 한다).

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

# [관전 포인트 1] tools=[] — 도구를 하나도 안 켜면 순수 대화만 하는 에이전트가 된다.
# [관전 포인트 2] max_budget_usd — 이 호출이 쓸 수 있는 최대 비용. 넘으면 중단된다(안전장치).
options = ClaudeAgentOptions(
    tools=[],
    system_prompt="You are a concise assistant. Answer in one short sentence.",
    max_turns=1,
    max_budget_usd=0.05,
)


async def main():
    # [관전 포인트 3] query()는 async generator — 진행 중 여러 메시지가 스트리밍으로 온다.
    #   (SystemMessage → AssistantMessage → ResultMessage 순. 자세한 건 2.streaming_messages.py)
    async for message in query(prompt="2 더하기 2는 몇이야?", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print("답변:", block.text)
        elif isinstance(message, ResultMessage):
            print(f"실제 비용: ${message.total_cost_usd:.4f} (턴 수: {message.num_turns})")


anyio.run(main)
