# pip install anthropic python-dotenv
#
# 6단계: 세 모델 비교 — haiku / sonnet / opus.
# 같은 질문을 세 모델에 보내 속도/길이를 비교한다.
#
# 모델 선택 가이드
#   - Haiku 4.5 : 가장 빠르고 저렴. 분류/요약/단순 작업, 대량 처리.
#   - Sonnet 4.6: 속도와 지능의 균형. 일반적인 작업 대부분.
#   - Opus 4.7  : 직전 세대 Opus. 4.8 과 요청 규격이 동일.
#   - Opus 4.8  : 가장 똑똑함. 복잡한 추론, 긴 호흡의 코딩/에이전트.
#
# ★ 요청 규격 차이 (모델마다 다르니 주의)  — Opus 4.7 과 4.8 은 규격이 같다.
#   기능                         | Haiku 4.5 | Sonnet 4.6 | Opus 4.7/4.8
#   temperature / top_p          |    O      |     O      |    X(400)
#   adaptive thinking            |    X      |     O      |     O
#   extended thinking(budget)    |    O      |     O      |     X
#   effort 파라미터              |    X      |     O      |     O

import os
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

models = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7", "claude-opus-4-8"]
prompt = "인공지능을 초등학생에게 한 문장으로 설명해줘."

for model in models:
    start = time.time()
    # temperature 를 일부러 안 쓴다: Opus 4.8 은 temperature 를 못 받는다(400).
    # 세 모델 공통으로 동작시키려면 temperature 를 빼는 게 안전하다.
    msg = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - start
    text = msg.content[0].text
    print(f"[{model}]  {elapsed:.1f}초, 출력 {msg.usage.output_tokens} 토큰")
    print(f"  {text}\n")
