"""
(2) Tool calling 신뢰도 비교 — Qwen 2.5 vs Qwen 3.5.

둘 다 tool calling 을 지원한다 — "추론(생각) 모드가 있어야 도구 호출이 된다"는 오해가 있는데
사실이 아니다. Qwen 2.5 도 이미 native tool calling 을 지원한다. 차이는 "인자를 정확히
채우는 신뢰도"다 — 같은 질문·같은 도구로 여러 번 반복 호출해서 실측으로 비교한다.

준비: pip install ollama  +  ollama pull qwen2.5:1.5b qwen3.5:2b
"""
import ollama

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "지정한 도시의 현재 날씨를 조회한다.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "도시 이름"}},
            "required": ["city"],
        },
    },
}]

QUESTION = "서울 날씨 어때?"
N = 5   # 모델당 반복 횟수 — 한 번의 성공/실패로 판단하지 않는다


def ask(model: str):
    resp = ollama.chat(model=model, messages=[{"role": "user", "content": QUESTION}], tools=TOOLS)
    return resp["message"].get("tool_calls")


def is_correct(calls) -> bool:
    if not calls:
        return False
    fn = calls[0]["function"]
    return fn["name"] == "get_weather" and "city" in fn["arguments"]


for model in ["qwen2.5:1.5b", "qwen3.5:2b"]:
    print(f"=== {model} ===")
    hits = 0
    for i in range(N):
        calls = ask(model)
        ok = is_correct(calls)
        hits += ok
        print(f"  시도 {i+1}: {'OK' if ok else '실패'} — {calls}")
    print(f"  → {hits}/{N} 성공\n")


# 정리:
#   - 둘 다 "도구를 부를 줄은 안다" — get_weather({'city': '서울'}) 형태를 만들 수 있다는
#     자체는 Qwen 2.5 에서도 확인된다. 즉 tool calling 은 3.5 전용 기능이 아니다.
#   - 실측 결과(아래)에서는 이 단순한 단일 도구·단일 인자 질문에서 둘 다 5/5 로 차이가 없었다 —
#     "2.5가 무조건 불안정하다"는 인상과 달리, 쉬운 케이스에선 2.5도 문제없이 잘 부른다.
#     알려진 이슈(ollama/ollama#7051, "Maybe" 패턴으로 인자를 헛짚는 경우)는 더 복잡하거나
#     모호한 요청에서 나타나는 경향이 있다 — 도구가 여러 개거나 인자가 여러 개인 상황으로
#     QUESTION/TOOLS 를 바꿔서 직접 실험해보면 차이가 드러날 수 있다.


# ─── 실행 결과 (실측, CPU) ───────────────────────────────────────
# === qwen2.5:1.5b ===
#   시도 1~5: 전부 OK — get_weather({'city': '서울'})
#   → 5/5 성공
#
# === qwen3.5:2b ===
#   시도 1~5: 전부 OK — get_weather({'city': '서울'})
#   → 5/5 성공
#
# (두 모델 다 이 단순한 케이스에서는 실패 없음 — 차이를 보려면 더 어려운 질문이 필요하다)


# ─── 참고: 같은 실험을 GPU 서버(RTX 4070 Laptop)에서 실측 ────────────────
# === qwen2.5:1.5b ===  (첫 호출 7.5초 — 모델 로딩 포함, 이후 0.7초대)
#   시도1 OK 7.5s  {'city': '서울'}
#   시도2 OK 0.7s  {'city': '서울'}
#   시도3 OK 0.7s  {'city': 'seoul'}      ← 영어 소문자로 답하기도 함
#   시도4 OK 0.7s  {'city': '서울'}
#   시도5 OK 0.7s  {'city': 'seoul'}
#   → 5/5 성공, 평균 2.0초
#
# === qwen3.5:2b ===  (전부 1~1.4초 — 이미 직전 실험에서 로딩된 상태)
#   시도1 OK 1.3s  {'city': '서울'}
#   시도2 OK 1.2s  {'city': 'Seoul, South Korea'}   ← 이번엔 3.5 쪽이 장황하게 답함
#   시도3 OK 1.2s  {'city': '서울'}
#   시도4 OK 1.0s  {'city': '서울'}
#   시도5 OK 1.4s  {'city': '서울'}
#   → 5/5 성공, 평균 1.2초
#
# → GPU에서는 성공률(5/5, 5/5)은 CPU와 같지만 속도는 완전히 다른 이야기다 — 모델이 한 번
#   VRAM에 올라간 뒤로는 초 단위가 아니라 **1초 남짓**으로 끝난다(CPU는 매 호출이 수 초).
#   또한 city 값이 매번 "서울"/"seoul"/"Seoul, South Korea"로 갈리는 것도 실측으로 확인된다 —
#   "성공"(city 키가 있음)과 "일관성"(같은 형식으로 채움)은 다른 문제라는 걸 보여준다.
