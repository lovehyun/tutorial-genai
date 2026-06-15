"""
(1) Modelfile 없이 '파이썬 코드'로 커스텀 모델 만들기 — ollama SDK 방식
    Modelfile.korean 과 똑같은 결과를, 파일 대신 SDK 로 생성한다.

    Modelfile 의 각 줄 ↔ create() 인자 대응:
      FROM qwen2.5:1.5b            →  from_="qwen2.5:1.5b"
      PARAMETER temperature 0.2   →  parameters={"temperature": 0.2, ...}
      SYSTEM \"\"\"...\"\"\"           →  system="..."

준비: pip install ollama  +  ollama pull qwen3.5:4b
실행: python 1.create_run.py
"""
import ollama

BASE = "qwen3.5:4b"
CUSTOM = "qwen-korean"   # 만들어질 커스텀 모델 이름

SYSTEM = """당신은 한국어 AI 비서입니다.

규칙:
- 질문이 어떤 언어로 들어오든 반드시 한국어 존댓말로만 답변
- 기술 질문은 예제 코드를 포함
- 단계별로 설명"""

# [1] 커스텀 모델 생성 — ollama create 와 동일한 일을 코드로.
#     이미 같은 이름이 있으면 덮어쓴다(설정만 바뀌므로 즉시 끝남, 재다운로드 X).
print(f"⚙  '{CUSTOM}' 생성 중 (FROM {BASE}) ...")
ollama.create(
    model=CUSTOM,
    from_=BASE,
    system=SYSTEM,
    parameters={"temperature": 0.2, "num_ctx": 8192, "top_p": 0.9},
)
print("✅ 생성 완료\n")

# [2] 바로 사용 — system 을 매번 안 붙여도 한국어 비서로 동작한다.
resp = ollama.chat(model=CUSTOM, messages=[
    {"role": "user", "content": "파이썬 리스트 컴프리헨션을 알려줘."}
])
print(resp["message"]["content"])

# 정리하고 싶다면:  ollama.delete(CUSTOM)   (CLI: ollama rm qwen-korean)
