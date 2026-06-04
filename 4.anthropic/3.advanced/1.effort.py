# pip install anthropic python-dotenv
#
# 고급 1: effort 파라미터 — 생각 깊이/토큰 소비를 조절한다.
# output_config={"effort": "low"|"medium"|"high"|"max"}  (high 가 기본)
# ★ Opus / Sonnet 4.6 만 지원. Haiku 4.5 / Sonnet 4.5 에 보내면 에러. "max" 는 Opus 전용.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

question = "정수론에서 페르마의 소정리를 직관적으로 설명해줘."

for effort in ("low", "high"):
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},     # ← 여기로 조절
        messages=[{"role": "user", "content": question}],
    )
    text = next((b.text for b in resp.content if b.type == "text"), "")
    print(f"=== effort={effort} | 출력 {resp.usage.output_tokens} 토큰 ===")
    print(text[:300], "...\n")
