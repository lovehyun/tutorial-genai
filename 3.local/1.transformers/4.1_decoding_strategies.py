# (4단계) 디코딩 전략 — '다음 토큰을 어떻게 고르나' 비교
# pip install transformers torch
#
# 2.2 에서 본 '다음 토큰 확률' 을 실제로 고르는 방법은 여러 가지다.
# 같은 프롬프트에 전략만 바꿔 결과가 어떻게 달라지는지 나란히 본다.

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

prompt = "Once upon a time"
inputs = tokenizer(prompt, return_tensors="pt")


def generate(**kwargs):
    set_seed(42)   # 샘플링 결과를 재현 가능하게 고정
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=40,
            pad_token_id=tokenizer.eos_token_id,
            **kwargs,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)


# [1] greedy — 매 단계 확률 1등만. 빠르고 일관적이나 반복·단조로움
print("=" * 70)
print("(1) Greedy  (do_sample=False)")
print("=" * 70)
print(generate(do_sample=False))

# [2] beam search — 여러 후보 경로를 동시에 탐색해 전체 확률 높은 문장 선택
print("\n" + "=" * 70)
print("(2) Beam search  (num_beams=5)")
print("=" * 70)
print(generate(num_beams=5, do_sample=False))

# [3] sampling + temperature — 확률대로 뽑기. temperature↑ = 더 과감/무작위
print("\n" + "=" * 70)
print("(3) Sampling  (temperature=1.2)")
print("=" * 70)
print(generate(do_sample=True, temperature=1.2))

# [4] top-k — 확률 상위 k개 후보 중에서만 샘플링 (엉뚱한 꼬리 차단)
print("\n" + "=" * 70)
print("(4) Top-k  (top_k=50)")
print("=" * 70)
print(generate(do_sample=True, top_k=50))

# [5] top-p (nucleus) — 누적확률 p 까지의 후보 중에서만 샘플링 (가장 많이 씀)
print("\n" + "=" * 70)
print("(5) Top-p  (top_p=0.92)")
print("=" * 70)
print(generate(do_sample=True, top_p=0.92))

# 정리:
#   | 전략        | 특징                         | 쓰는 곳            |
#   | greedy      | 1등만, 항상 같음, 반복 위험    | 분류·요약(정확성)   |
#   | beam        | 여러 경로 탐색, 안정적          | 번역·요약          |
#   | sampling/T  | 확률대로, 창의적, T로 과감함 조절 | 스토리·대화        |
#   | top-k/top-p | 후보를 추려 샘플링 (품질↑)      | 대화·창작 기본값    |
#   - temperature·top_k·top_p 는 보통 함께 조합해서 쓴다
#   - 다음(5.x): 이 모든 게 가능한 이유 = 어텐션. 모델 내부를 들여다본다
