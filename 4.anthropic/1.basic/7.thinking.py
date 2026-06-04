# pip install anthropic python-dotenv
#
# 7단계: 생각하기(thinking) — 모델이 답하기 전에 내부 추론을 한다.
# ★ 방식이 모델마다 다르다 (확인 안 하면 400 난다):
#   - Haiku 4.5  : "extended thinking" → thinking={"type":"enabled","budget_tokens":N}
#                  budget_tokens 는 max_tokens 보다 작아야 하고 최소 1024.
#                  Haiku 는 adaptive 를 지원하지 않는다.
#   - Sonnet 4.6 : adaptive 권장 → thinking={"type":"adaptive"}
#   - Opus 4.8   : adaptive 만 가능 → thinking={"type":"adaptive"}
#                  (Opus 는 budget_tokens 방식이 제거됨)
#
# 공통 주의: thinking 을 켜면 content 에 'thinking' 블록이 'text' 블록보다 먼저 올 수 있다.
#           → content[0].text 로 바로 꺼내지 말고 block.type 으로 걸러서 text 만 뽑는다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

question = "사과 3개에 1500원이면 사과 7개는 얼마? 계산 과정도 보여줘."

def show(message):
    """생각(thinking) 블록과 답변(text) 블록을 둘 다 출력한다."""
    for block in message.content:
        if block.type == "thinking":
            print("[생각]\n" + block.thinking + "\n")
        elif block.type == "text":
            print("[답변]\n" + block.text + "\n")

# (1) Opus 4.8 — adaptive thinking
#     ★ Opus 4.7/4.8 은 생각 텍스트가 기본적으로 비어 있다("omitted").
#       생각을 실제로 보려면 display:"summarized" 를 줘야 한다.
print("=== Opus 4.8 (adaptive, 생각 요약 표시) ===")
msg = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=2000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[{"role": "user", "content": question}],
)
show(msg)

# (2) Haiku 4.5 — extended thinking (budget_tokens). budget_tokens < max_tokens.
#     Haiku 는 생각 텍스트가 기본으로 들어온다(display 옵션 없음).
print("=== Haiku 4.5 (budget_tokens) ===")
msg = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=2000,
    thinking={"type": "enabled", "budget_tokens": 1024},
    messages=[{"role": "user", "content": question}],
)
show(msg)

# 참고: adaptive 는 쉬운 질문이면 모델이 생각을 건너뛸 수 있어 thinking 블록이 없을 수도 있다.
# 참고: Opus/Sonnet 은 effort 로 생각 깊이/토큰을 조절할 수 있다 (Haiku 는 effort 미지원).
#   output_config={"effort": "low"|"medium"|"high"|"max"}   # max 는 Opus 전용
