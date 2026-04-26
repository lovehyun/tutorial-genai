"""
한국어 대화 생성 — Ollama 기반 최신 한국어 모델 비교
- 설치: ollama pull exaone3.5:2.4b && ollama pull qwen3:4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"


def chat(model, messages, temperature=0.7):
    """Ollama 챗 API 호출"""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        },
    )
    return response.json()["message"]["content"]


def demo_single_turn():
    """단일 턴 대화 — 모델별 비교"""
    print("=" * 50)
    print("  단일 턴 대화: 모델별 응답 비교")
    print("=" * 50)

    question = "인공지능이 우리 생활을 어떻게 바꾸고 있는지 3가지만 설명해주세요."
    models = ["exaone3.5:2.4b", "qwen3:4b"]

    for model in models:
        print(f"\n[ {model} ]")
        print("-" * 40)
        try:
            result = chat(
                model,
                [
                    {"role": "system", "content": "당신은 친절한 한국어 AI 어시스턴트입니다. 간결하게 답변하세요."},
                    {"role": "user", "content": question},
                ],
            )
            print(result)
        except Exception as e:
            print(f"  오류: {e}")
            print(f"  → 'ollama pull {model}' 로 모델을 먼저 다운로드하세요.")


def demo_multi_turn():
    """멀티 턴 대화 — 히스토리 유지"""
    print("\n" + "=" * 50)
    print("  멀티 턴 대화: 대화 히스토리 유지")
    print("=" * 50)

    model = "exaone3.5:2.4b"
    messages = [
        {"role": "system", "content": "당신은 한국 역사 전문가입니다. 간결하게 답변하세요."},
    ]

    questions = [
        "조선시대는 언제부터 언제까지인가요?",
        "그 시대의 가장 위대한 왕은 누구인가요?",
        "그 왕의 대표적인 업적 3가지를 알려주세요.",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[사용자] {question}")
        messages.append({"role": "user", "content": question})

        try:
            reply = chat(model, messages)
            print(f"[AI] {reply}")
            messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"  오류: {e}")
            break

    print(f"\n  총 대화 턴: {len([m for m in messages if m['role'] == 'user'])}회")


def demo_persona():
    """페르소나 설정 — 시스템 프롬프트로 캐릭터 부여"""
    print("\n" + "=" * 50)
    print("  페르소나 설정: 시스템 프롬프트 활용")
    print("=" * 50)

    model = "qwen3:4b"
    question = "요즘 취업이 너무 힘들어요. 어떻게 해야 할까요?"

    personas = [
        ("할머니 상담사", "당신은 따뜻한 한국 할머니입니다. 손주에게 이야기하듯 다정하고 지혜로운 조언을 해주세요. 2~3문장으로 답변하세요."),
        ("IT 멘토", "당신은 10년차 IT 개발자 멘토입니다. 실용적이고 구체적인 커리어 조언을 해주세요. 2~3문장으로 답변하세요."),
        ("철학자", "당신은 동양 철학을 전공한 철학자입니다. 깊은 통찰과 비유로 답변하세요. 2~3문장으로 답변하세요."),
    ]

    for name, system_prompt in personas:
        print(f"\n[ {name} ]")
        print("-" * 40)
        try:
            result = chat(
                model,
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
            )
            print(result)
        except Exception as e:
            print(f"  오류: {e}")


# ── 학습 포인트 ──

def print_learning_points():
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. Ollama REST API: /api/chat 엔드포인트로 로컬 LLM과 대화
   - messages 배열에 system/user/assistant 역할을 구분
   - stream: false로 전체 응답을 한 번에 수신

2. 모델 비교: 동일 프롬프트로 여러 모델의 한국어 품질 비교
   - EXAONE 3.5: 한국어 자연스러움 최고
   - Qwen3: 오픈 라이선스(Apache 2.0) + 다국어 균형

3. 멀티 턴 대화: messages 배열에 이전 대화를 누적하여 맥락 유지
   - 매 턴마다 assistant 응답을 히스토리에 추가

4. 페르소나: system 프롬프트로 AI의 성격/전문성/말투를 제어
   - 동일 질문이라도 페르소나에 따라 완전히 다른 답변 생성
""")


if __name__ == "__main__":
    demo_single_turn()
    demo_multi_turn()
    demo_persona()
    print_learning_points()
