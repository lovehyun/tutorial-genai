"""
(1) 기본 대화 — EXAONE 3.5 와 단일/멀티 턴 대화
EXAONE 3.5 = LG AI Research 의 한국어 강한 오픈 LLM (Ollama 로 로컬 실행).
호출은 ollama 파이썬 SDK 사용 (REST 대비 간단 — 비교는 6.ollama1_restapi vs 6.ollama2_sdk).

준비: pip install ollama  +  ollama pull exaone3.5   (가벼운 버전: exaone3.5:2.4b)
"""
import ollama

MODEL = "exaone3.5:latest"   # 가벼운 버전: "exaone3.5:2.4b"


def chat(messages, temperature=0.7):
    return ollama.chat(model=MODEL, messages=messages,
                       options={"temperature": temperature})["message"]["content"]


# 1) 단일 턴
print("=" * 50, "\n 단일 턴 대화\n", "=" * 50)
print(chat([
    {"role": "system", "content": "당신은 친절한 한국어 AI 어시스턴트입니다. 간결히 답하세요."},
    {"role": "user", "content": "EXAONE 모델의 특징을 한 문장으로 알려줘."},
]))

# 2) 멀티 턴 — 이전 대화를 messages 에 누적해 맥락 유지
print("\n" + "=" * 50, "\n 멀티 턴 대화 (맥락 유지)\n", "=" * 50)
messages = [{"role": "system", "content": "당신은 한국 음식 전문가입니다. 간결히 답하세요."}]
for q in ["비빔밥의 주재료는?", "방금 말한 음식에 어울리는 국은?", "그걸 영어로 뭐라고 해?"]:
    print(f"\n[사용자] {q}")
    messages.append({"role": "user", "content": q})
    reply = chat(messages)
    print(f"[EXAONE] {reply}")
    messages.append({"role": "assistant", "content": reply})

# 학습 포인트:
#   - ollama.chat(model, messages) — system/user/assistant 역할 배열을 넘긴다
#   - 멀티 턴은 직접 messages 에 이전 응답을 누적하면 된다 (서버는 상태를 기억 안 함)
