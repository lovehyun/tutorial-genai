"""
(4) <think>/<answer> 태그 활용 — Modelfile.reasoning 의 실전 payoff
    SYSTEM 으로 출력 '형식'을 고정해두면, 앱에서 추론과 최종답을 분리해 쓸 수 있다.
      예) 추론 과정은 접어두고 <answer> 만 사용자에게 보여주기.

전제: ollama create gemma4-korean -f Modelfile.reasoning   (또는 bash build.sh)
실행: python 4.reasoning_parse.py
"""
import re
import ollama

MODEL = "gemma4-korean"

resp = ollama.chat(model=MODEL, messages=[
    {"role": "user", "content": "재귀와 반복문의 차이를 설명해줘."}
])
text = resp["message"]["content"]

# 태그를 정규식으로 분리 (형식이 고정돼 있으니 파싱이 단순하다)
def grab(tag, s):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", s, re.DOTALL)
    return m.group(1).strip() if m else None

think = grab("think", text)
answer = grab("answer", text)

print("🧠 추론 과정 (think) ─ 보통 UI 에선 접어둠")
print(think or "(태그 없음 — 모델이 형식을 안 지킴)")
print("\n💬 최종 답변 (answer) ─ 사용자에게 보여줄 부분")
print(answer or text)   # 태그가 없으면 원문 전체로 폴백

# 포인트:
#   - 같은 모델이라도 SYSTEM 규칙으로 '구조화된 출력'을 유도할 수 있다.
#   - 혹시 모델이 형식을 안 지킬 때를 대비해 위처럼 폴백(원문 그대로)을 두면 안전.
