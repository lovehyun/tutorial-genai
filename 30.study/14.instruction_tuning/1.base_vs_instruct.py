"""
Instruction Tuning(RLHF의 앞단계) — 같은 아키텍처, 다른 학습이 만드는 차이
- 설치: pip install transformers torch

지금까지 본 사전학습(pretraining)은 "다음 토큰 맞히기"만 반복한다(`11.training_objectives`) —
그 결과물(base 모델)은 "그럴듯하게 이어쓰기"는 잘하지만 "질문에 답하기"나 "지시를 따르기"는
배운 적이 없다. Instruction tuning은 그 base 모델에 (지시, 좋은 응답) 쌍을 추가로 학습시켜
"질문하면 답한다"는 대화 형식 자체를 가르친다. RLHF(사람 피드백으로 강화학습)는 그 위에 한
단계 더 얹어 "어떤 응답이 더 나은가"까지 학습시키는 것 — 여기서는 그 앞단계인 instruction
tuning의 **효과**를 base 모델과 직접 비교해서 확인한다(RLHF 자체를 재현하지는 않는다 — 강화학습
루프는 이 저장소 규모를 넘어선다).
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

BASE_MODEL = "TinyLlama/TinyLlama_v1.1"                 # instruction tuning '이전' — 순수 사전학습만
INSTRUCT_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"    # instruction tuning '이후' — 대화형으로 추가 학습됨
# 같은 팀(TinyLlama)이 같은 아키텍처·크기로 두 버전을 공개해서, "학습 방식 차이"만 순수하게 비교할 수 있다.


def ask_base(prompt: str) -> str:
    """[관전 포인트 1] base 모델 — 프롬프트를 그냥 '이어쓸 텍스트'로 취급한다. 지시를 따르지 않는다."""
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.float32)
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=60, do_sample=False)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def ask_instruct(prompt: str) -> str:
    """[관전 포인트 2] instruct 모델 — 채팅 템플릿(apply_chat_template)으로 감싸야 제대로 동작한다.
    "역할이 있는 대화"라는 형식 자체가 instruction tuning으로 학습된 것이라, 그 형식을 지켜줘야 한다."""
    tokenizer = AutoTokenizer.from_pretrained(INSTRUCT_MODEL)
    model = AutoModelForCausalLM.from_pretrained(INSTRUCT_MODEL, dtype=torch.float32)
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=80, do_sample=False)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def main():
    prompt = "List three benefits of regular exercise."

    print("=" * 60)
    print("  Base 모델 vs Instruction-tuned 모델")
    print("=" * 60)
    print(f"\n  같은 질문: \"{prompt}\"\n")

    print("[ 1. Base 모델 (TinyLlama_v1.1, instruction tuning 이전) ]")
    print("-" * 40)
    base_answer = ask_base(prompt)
    print(base_answer)

    print("\n[ 2. Instruct 모델 (TinyLlama-1.1B-Chat, instruction tuning 이후) ]")
    print("-" * 40)
    instruct_answer = ask_instruct(prompt)
    print(instruct_answer)

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 두 모델은 아키텍처·파라미터 수가 완전히 같다(둘 다 TinyLlama 1.1B) — 차이는 오직
   "무엇으로 추가 학습했는가"뿐이다. 그런데도 행동이 완전히 다르다(위 실행 결과 직접 비교).

2. Base 모델이 지시를 무시하는 건 "멍청해서"가 아니다:
   - 사전학습 목표(`11.training_objectives`)는 "다음 토큰 맞히기"뿐이었다
   - "List three benefits of exercise."라는 문장 다음에 뭐가 오는지는 학습 데이터(인터넷 텍스트)
     안에서 다양했을 것이다 — 실제로 답이 나올 수도, 전혀 다른 주제로 새는 것도 '통계적으로
     그럴듯하면' 다 나올 수 있다. "질문엔 답해야 한다"는 규칙 자체를 배운 적이 없다.

3. Instruction tuning이 가르치는 것:
   - (지시, 좋은 응답) 쌍을 모아 "이런 형식의 입력엔 이런 형식으로 답한다"를 추가로 학습시킨다
   - 채팅 템플릿(`<|user|>...<|assistant|>` 같은 특수 태그)도 이 단계에서 학습된 "약속"이라,
     그 형식을 안 지키고 넣으면 instruct 모델도 base처럼 동작할 수 있다(위 코드에서
     `apply_chat_template`을 쓴 이유).

4. RLHF는 여기서 한 단계 더 간다:
   - Instruction tuning까지는 "정답 예시를 그대로 따라 하기"(지도학습)다
   - RLHF는 같은 질문에 대해 모델이 낸 여러 답을 사람이(또는 사람을 흉내낸 보상모델이) 비교
     평가하고, "더 선호되는 답"을 내도록 강화학습으로 추가 조정한다 — 정답을 베끼는 게 아니라
     "무엇이 더 나은가"라는 기준 자체를 학습시키는 것. 이 저장소에서 그 강화학습 루프까지
     재현하지는 않지만, 그 앞단계(instruction tuning)의 효과만으로도 위처럼 극적인 차이가
     생긴다는 걸 확인했다.
""")


if __name__ == "__main__":
    main()
