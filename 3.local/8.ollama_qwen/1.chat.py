"""
(1) 대화 — Qwen 으로 단일/멀티 턴 채팅 (한국어 vs 영어 비교)
호출은 ollama 파이썬 SDK 사용 (REST 대비 간단 — 비교는 6.ollama1_restapi vs 6.ollama2_sdk).
준비: pip install ollama  +  ollama pull qwen2.5:1.5b   (더 좋은 품질: qwen2.5:7b / qwen3:4b)
"""
import ollama

MODEL = "qwen2.5:1.5b"


def chat(messages):
    return ollama.chat(model=MODEL, messages=messages)["message"]["content"]


# 같은 질문을 한국어 / 영어로 — 작은 모델의 언어별 품질 차이를 비교
print("[단일 턴 — 한국어]")
print(chat([{"role": "user", "content": "인공지능을 한 문장으로 설명해줘."}]))

print("\n[단일 턴 — English]")
print(chat([{"role": "user", "content": "Explain artificial intelligence in one sentence."}]))

# 멀티 턴 — 이전 대화를 messages 에 누적하면 맥락이 유지된다
print("\n[멀티 턴 — 한국어]")
messages = [{"role": "system", "content": "간결한 한국어로 답하세요."}]
for q in ["비빔밥의 주재료는?", "방금 그 음식에 어울리는 국은?"]:
    messages.append({"role": "user", "content": q})
    reply = chat(messages)
    print(f"Q: {q}\nA: {reply}\n")
    messages.append({"role": "assistant", "content": reply})

# 핵심: ollama.chat(model, messages) 한 줄, 멀티턴은 messages 직접 누적
#
# [관찰 — qwen2.5:1.5b 로 직접 실행]
#   영어 답변은 자연스럽지만 한국어 대화는 오류·깨진 표현이 잦다(예: 비빔밥 재료를 엉뚱하게 답함).
#   작은 다국어 모델의 전형적 한계 → 한국어 품질이 필요하면 qwen2.5:7b / qwen3 로 MODEL 만 교체.
