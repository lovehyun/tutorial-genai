# (7단계) 생성 모델 품질 평가 — Perplexity
# pip install transformers torch numpy
#
# 지금까지는 "그럴듯해 보이는 문장이 나오는지" 눈으로만 확인했다. 실전에서는 숫자로 비교해야
# 한다 — 그 기본 지표가 Perplexity(PPL)다. "모델이 이 문장을 보고 얼마나 안 놀랐는가"를
# 수치화한 것 — 낮을수록 모델이 그 텍스트를 '자연스럽다'고 느낀다는 뜻이다.
#
# 원리: cross-entropy loss(다음 토큰 예측이 틀린 정도, 2.2_logits_next_token.py 참고)의
# 지수(exp)를 취한 것뿐이다. loss가 0이면 PPL=1(완벽하게 예측), loss가 클수록 PPL도 커진다.

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()


def perplexity(text: str) -> float:
    """텍스트 하나의 perplexity를 계산한다 — loss(cross-entropy)의 지수를 취할 뿐."""
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        # labels=input_ids 를 주면 모델이 자동으로 "다음 토큰 예측 loss"를 계산해준다
        # (11.training_objectives/1.objectives_compare.py 의 causal_lm_targets() 와 같은 방식)
        outputs = model(**inputs, labels=inputs["input_ids"])
    return torch.exp(outputs.loss).item()


# [관전 포인트] 자연스러운 문장 vs 문법은 맞지만 뜬금없는 문장 vs 단어를 무작위로 섞은 문장
samples = {
    "자연스러운 문장": "The sun rises in the east and sets in the west every day.",
    "문법은 맞지만 뜬금없는 문장": "The sun calculates purple mathematics inside a triangular refrigerator.",
    "단어를 무작위로 섞은 문장": "sets sun the day the every east rises and in west in",
}

print(f"{'문장 종류':<28} {'Perplexity':>12}")
print("-" * 42)
for label, text in samples.items():
    ppl = perplexity(text)
    print(f"{label:<28} {ppl:>12.2f}")
    print(f"  → \"{text}\"")

# 정리 (실측 결과 기준 — 자연스러운 문장 14.08 < 무작위로 섞은 문장 1073.32 < 문법은 맞지만
# 뜬금없는 문장 5643.65):
#   - PPL이 낮을수록 모델이 "말이 되는 문장"이라고 판단한 것 — 자연스러운 문장이 가장 낮게 나와야 정상,
#     실측에서도 압도적으로 가장 낮다(14.08, 나머지 둘의 1/70~1/400 수준)
#   - 흥미로운 지점은 무작위로 섞은 문장(1073)이 문법은 맞지만 뜬금없는 문장(5643)보다 오히려 덜
#     놀랍다는 것 — perplexity는 "문법이 맞는가"가 아니라 "이 단어 조합을 학습 데이터에서 얼마나
#     자주 봤는가"를 재는 지표라서 그렇다. 섞인 문장도 sun/day/east/west/rises 같은 흔한 단어들의
#     지역적 조합("the day", "east rises")은 학습 데이터에 흔했던 반면, "sun calculates"나
#     "purple mathematics" 같은 조합은 문법적으로는 멀쩡해도 의미적으로 한 번도 같이 나온 적이
#     없다시피 해서 모델이 훨씬 더 "놀란다" — PPL이 곧 문법 검사기가 아니라는 걸 보여주는 실측 증거다.
#   - 실전에서는 이걸로 "파인튜닝 전후 모델이 실제로 더 좋아졌는지"를 검증 데이터셋 전체에 대해
#     평균 내서 비교한다 — LoRA(2.mymodel/3.lora) 나 경량화(2.mymodel/2.compression) 후에도
#     "눈으로 보기엔 비슷한데 실제로는 어떤가"를 이 지표로 확인할 수 있다.
#   - 단, PPL이 낮다고 "더 똑똑한 모델"인 건 아니다 — 그저 "이 텍스트 분포에 얼마나 익숙한가"일
#     뿐이라, 서로 다른 토크나이저·모델 간 PPL을 직접 비교하는 건 위험하다(같은 모델 내에서
#     전/후 비교, 또는 같은 조건의 후보 비교에 쓰는 게 정석이다).
