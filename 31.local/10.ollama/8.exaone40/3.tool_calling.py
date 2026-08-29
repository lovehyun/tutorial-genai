"""
(2) Tool calling — EXAONE 3.5 에는 없던, EXAONE 4.0 의 진짜 핵심 신기능.

../7.exaone35/README.md 에 이렇게 적혀 있다: "EXAONE 3.5 는 네이티브 tool calling(함수호출)을
지원하지 않습니다." EXAONE 4.0 은 이 한계를 해결했다 — LG 공식 발표에도 agentic tool use,
Function Calling, MCP 지원이 명시돼 있다.

그런데 실측해보면 한 가지 반전이 있다: **같은 EXAONE 4.0 인데 어느 커뮤니티 GGUF를
쓰느냐에 따라 실제로 되기도 하고 안 되기도 한다.** 이 파일이 그 차이를 그대로 보여준다.

준비: pip install ollama
  ollama pull ingu627/exaone4.0:1.2b
  ollama pull sam860/exaone-4.0:1.2b
"""
import ollama

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "지정한 도시의 현재 날씨를 조회한다.",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    },
}]

QUESTION = "서울 날씨 어때?"
N = 3

for model in ["ingu627/exaone4.0:1.2b", "sam860/exaone-4.0:1.2b"]:
    print(f"=== {model} ===")
    hits = 0
    for i in range(N):
        resp = ollama.chat(model=model, messages=[{"role": "user", "content": QUESTION}], tools=TOOLS)
        calls = resp["message"].get("tool_calls")
        ok = bool(calls) and calls[0]["function"]["name"] == "get_weather"
        hits += ok
        if ok:
            print(f"  시도{i+1}: OK — {calls}")
        else:
            print(f"  시도{i+1}: 실패 — 도구를 안 부르고 이렇게 답함: {resp['message'].content[:80]!r}...")
    print(f"  → {hits}/{N} 성공\n")


# 정리:
#   - **같은 "EXAONE 4.0"이라는 이름인데 결과가 극과 극이다.** ollama.show() 로 둘 다
#     "tools" capability 가 선언돼 있는 건 똑같은데, 실측 성공률은 하늘과 땅 차이다.
#   - 원인은 모델 가중치 자체가 아니라 **Ollama Modelfile 템플릿(도구 스키마를 프롬프트에
#     주입하는 방식)을 업로더가 얼마나 정확히 맞췄는가**에 있을 가능성이 높다 — 공식
#     라이브러리(Qwen 3.5)에는 없는, 커뮤니티 업로드 특유의 리스크다.
#   - **실전 교훈**: "capability: tools" 가 ollama.show() 에 찍혀 있다고 안심하지 말고,
#     실제로 몇 번 호출해서 확인(smoke test)해야 한다 — 이 파일처럼 3~5회만 돌려봐도
#     바로 드러난다.
#   - 그래도 결론적으로 **EXAONE 4.0은 (제대로 된 GGUF를 쓰면) tool calling이 된다** —
#     EXAONE 3.5의 가장 큰 약점이 4.0에서 해소됐다는 것 자체는 실측으로 확인됐다.


# ─── 실행 결과 (실측, CPU) ───────────────────────────────────────
# === ingu627/exaone4.0:1.2b ===
#   시도1: 실패 — '음, 서울 날씨에 대한 질문이군. 사용자가 현재 서울의 날씨 상태를...'
#   시도2: 실패 — '음, 사용자가 서울 날씨를 물어보고 있군. 아마도 오늘 날씨에 대해...'
#   시도3: 실패 — '아, 서울 날씨를 물어보는 사용자네. 최근 서울이 정말 복잡했나 보다...'
#   → 0/3 성공  (셋 다 도구 호출 없이 "날씨 앱으로 확인해봤는데..." 식으로 지어내 답했다)
#
# === sam860/exaone-4.0:1.2b ===
#   시도1: OK — get_weather({'city': '서울'})
#   시도2: OK — get_weather({'city': '서울'})
#   시도3: OK — get_weather({'city': '서울'})
#   → 3/3 성공


# ─── 참고: 같은 실험을 GPU 서버(RTX 4070 Laptop)에서 실측 ────────────────
# sam860/exaone-4.0:1.2b — 3/3 성공, 각 1.1초/1.3초/0.9초 (CPU 대비 훨씬 빠름)
#   단, city 값이 이번엔 전부 "Seoul"(영어)로 나왔다 — CPU에서는 "서울"(한글)이었다.
#   "성공"(도구를 부름) 자체는 하드웨어와 무관하게 재현되지만, 인자를 어떤 언어/형식으로
#   채우는지는 실행마다 달라질 수 있다는 걸 보여준다.
