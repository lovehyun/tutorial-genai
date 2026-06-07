# (2단계) logits → 다음 토큰 확률 — '생성' 이 실제로 일어나는 원리
# pip install transformers torch
#
# 2.1(hidden state) 다음: 생성 모델(GPT-2)은 hidden state 위에 'LM 헤드' 를 얹어
#   어휘 전체에 대한 점수(logits) 를 낸다. softmax 하면 '다음 토큰 확률' 이 된다.
#   → 텍스트 생성 = 이 다음-토큰-뽑기를 반복하는 것뿐이다.

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# AutoModelForCausalLM = 본체 + LM 헤드 (다음 토큰 예측용)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

prompt = "The capital of France is"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

# [관전 포인트 1] logits 모양 = [배치, 토큰수, 어휘수]
#   각 위치마다 '다음에 올 토큰' 점수를 어휘 전체(50257개)에 대해 매긴다.
print(f"logits shape: {tuple(logits.shape)}  ← [batch, tokens, vocab={model.config.vocab_size}]")

# [관전 포인트 2] 우리가 원하는 건 '맨 마지막 위치' 의 다음 토큰 예측
next_token_logits = logits[0, -1, :]            # 마지막 토큰 다음 예측
probs = torch.softmax(next_token_logits, dim=-1)  # 점수 → 확률

# [관전 포인트 3] 확률 상위 5개 후보 = 모델이 보기에 그럴듯한 다음 단어
top = torch.topk(probs, 5)
print(f"\n프롬프트: '{prompt}'")
print("다음 토큰 후보 Top-5:")
for prob, idx in zip(top.values, top.indices):
    print(f"  {tokenizer.decode([idx])!r:12} 확률 {prob.item():.3f}")

# [관전 포인트 4] greedy = 그냥 1등을 고르는 것
best = top.indices[0]
print(f"\ngreedy 선택 → {tokenizer.decode([best])!r}")
print(f"이어진 문장: '{prompt}{tokenizer.decode([best])}'")

# 정리:
#   - 생성 = (입력 → logits → 다음 토큰 1개 선택 → 입력에 붙이기) 의 반복
#   - '어떻게 1개를 고르냐' 가 곧 디코딩 전략 (1등? 확률대로 뽑기? 상위 몇 개 중에서?)
#   - 다음(3.x): 두 모델 유형 — 인코더(빈칸채우기) vs 디코더(생성) → 4.1 디코딩 전략
