# pip install anthropic python-dotenv
#
# 5단계: 자주 쓰는 파라미터.
#   - max_tokens : 응답 최대 길이(필수). 모자라면 답이 중간에 잘린다(stop_reason="max_tokens").
#   - temperature: 0=일관/보수적, 높을수록 다양/창의적. 범위 0.0~1.0.
#
# ⚠️ 모델별 주의 (중요)
#   - temperature / top_p 는 Haiku 4.5, Sonnet 4.6 에서 사용 가능.
#   - 단, Opus 4.7/4.8 에서는 제거되어 보내면 400 에러! (Opus 는 프롬프트로 조절한다)
#   - temperature 와 top_p 를 "동시에" 보내면 Claude 4 계열 전부 400. 둘 중 하나만 쓴다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5"   # temperature 를 쓰므로 Haiku/Sonnet 사용 (Opus 아님)
prompt = "AI 를 한 문장으로 비유해줘."

for temp in (0.0, 1.0):
    print(f"--- temperature={temp} ---")
    msg = client.messages.create(
        model=MODEL,
        max_tokens=100,
        temperature=temp,
        messages=[{"role": "user", "content": prompt}],
    )
    print(msg.content[0].text, "\n")
