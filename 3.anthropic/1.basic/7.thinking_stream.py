# pip install anthropic python-dotenv
#
# 7-2단계: 생각(thinking)을 "스트리밍"으로 실시간 보기.
# 7.thinking.py 는 호출이 끝난 뒤 블록을 출력했지만, 여기서는 생성되는 대로 흘려 받는다.
# 스트림 이벤트에서 thinking_delta(생각 조각) / text_delta(답변 조각) 를 구분해 출력한다.
#
# ★ Opus 4.7/4.8 은 생각이 기본 "omitted" 라 display:"summarized" 를 줘야 생각이 흐른다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

question = "12 x 13 을 암산으로 어떻게 푸는지 단계별로 설명해줘."

with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=2000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[{"role": "user", "content": question}],
) as stream:
    for event in stream:
        # 블록이 시작될 때 어떤 종류인지 헤더를 찍어준다
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("\n[생각] ", end="", flush=True)
            elif event.content_block.type == "text":
                print("\n\n[답변] ", end="", flush=True)
        # 블록 내용이 조각조각 들어온다 — 종류에 맞게 출력
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)

print()
