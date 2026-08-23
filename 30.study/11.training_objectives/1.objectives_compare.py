"""
학습 목적함수(Training Objective) — GPT와 BERT는 애초에 "다른 문제"를 풀도록 학습됐다
- 설치: pip install transformers torch matplotlib numpy

`31.local/1.transformers/3.1_encoder_fillmask.py`(BERT 빈칸 채우기)와 `3.2_decoder_generate.py`
(GPT 생성)는 두 모델이 "이미 학습된 뒤" 어떻게 다르게 동작하는지 보여줬다. 여기서는 한 단계
더 들어가서, **애초에 학습할 때 무엇을 맞히도록 시켰는지**(loss가 어디서 계산되는지)를 직접
계산해서 확인한다 — 이 차이가 두 모델의 성격 차이(이해 vs 생성)를 만든 근본 원인이다.
"""
import os
import warnings
import numpy as np
import torch
import matplotlib
import matplotlib.pyplot as plt
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForMaskedLM,
)

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

SENTENCE = "The cat sat on the mat"


def causal_lm_targets():
    """GPT류(Causal LM) — '다음 토큰 예측'. 매 위치가 '바로 다음 토큰'을 맞혀야 한다.

    핵심: labels를 입력과 '한 칸 밀어서' 준다 — position i의 예측 대상은 token[i+1]이다.
    라이브러리 내부에서 이 shift를 자동으로 해주지만, 여기서는 직접 눈으로 보려고 수동으로도 만든다.
    """
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    model.eval()

    inputs = tokenizer(SENTENCE, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    with torch.no_grad():
        # labels=input_ids 를 주면 모델이 내부적으로 한 칸 shift해서 loss를 계산한다.
        out = model(**inputs, labels=inputs["input_ids"])

    # 수동으로도 확인: position i는 token[i+1]을 맞혀야 한다 (마지막 위치는 맞힐 대상이 없음)
    targets = [tokens[i + 1] if i + 1 < len(tokens) else None for i in range(len(tokens))]

    print(f"  입력 토큰:        {tokens}")
    print(f"  각 위치의 예측대상: {targets}   (마지막은 맞힐 다음 토큰이 없어 loss 제외)")
    print(f"  loss (cross-entropy, 평균): {out.loss.item():.3f}")
    print("  → 모든 위치(마지막 제외)가 loss에 기여한다 — '전부 다음 것 맞히기'")

    return tokens, targets, out.loss.item()


def masked_lm_targets():
    """BERT류(Masked LM) — 일부 토큰을 [MASK]로 가리고 '그 자리'만 맞힌다.

    핵심: 가린 위치만 loss에 기여한다 — 안 가린 위치는 정답을 이미 보고 있으니 맞히는 게 의미 없다.
    """
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")
    model.eval()

    inputs = tokenizer(SENTENCE, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    labels = inputs["input_ids"].clone()

    # [관전 포인트] 토큰 중 일부(여기선 "sat", "mat")를 [MASK]로 바꾸고, 나머지 위치의
    #   label은 -100으로 지정 — HuggingFace 컨벤션에서 -100은 "이 위치는 loss 계산에서 제외"라는 뜻.
    mask_positions = [i for i, t in enumerate(tokens) if t in ("sat", "mat")]
    masked_input = inputs["input_ids"].clone()
    for pos in mask_positions:
        masked_input[0, pos] = tokenizer.mask_token_id

    loss_labels = torch.full_like(labels, -100)
    for pos in mask_positions:
        loss_labels[0, pos] = labels[0, pos]

    with torch.no_grad():
        out = model(input_ids=masked_input, attention_mask=inputs["attention_mask"], labels=loss_labels)

    masked_tokens = tokenizer.convert_ids_to_tokens(masked_input[0])
    contributes = [tokens[i] if i in mask_positions else None for i in range(len(tokens))]

    print(f"  입력 토큰(마스킹 후): {masked_tokens}")
    print(f"  각 위치의 예측대상:   {contributes}   (마스킹 안 된 자리는 -100 → loss 제외)")
    print(f"  loss (cross-entropy, 마스킹된 자리만 평균): {out.loss.item():.3f}")
    print("  → [MASK] 자리만 loss에 기여한다 — '가려진 것만 맞히기', 양쪽 문맥을 다 보고 맞힌다")

    return tokens, mask_positions, out.loss.item()


def plot_loss_contribution(causal_tokens, causal_targets, mlm_tokens, mlm_mask_positions,
                            filename="results/1.loss_contribution.png"):
    """어느 위치가 loss에 기여하는지 — Causal LM(전부) vs Masked LM(가려진 자리만) 시각 비교."""
    # GPT-2 BPE 토큰의 'Ġ'는 "이 토큰 앞에 공백이 있었다"는 표시일 뿐이라 그림에서는 지운다.
    causal_labels = [t.replace("Ġ", "") for t in causal_tokens]

    fig, axes = plt.subplots(2, 1, figsize=(12, 6))

    # Causal LM: 마지막 위치 빼고 전부 기여
    causal_contrib = [1 if t is not None else 0 for t in causal_targets]
    colors1 = ["#55A868" if c else "#CCCCCC" for c in causal_contrib]
    axes[0].bar(range(len(causal_tokens)), [1] * len(causal_tokens), color=colors1)
    axes[0].set_xticks(range(len(causal_tokens)))
    axes[0].set_xticklabels(causal_labels)
    axes[0].set_yticks([])
    axes[0].set_title("Causal LM(GPT) — 거의 모든 위치가 loss에 기여(다음 토큰 예측)")

    # Masked LM: 마스킹된 위치만 기여
    mlm_contrib = [1 if i in mlm_mask_positions else 0 for i in range(len(mlm_tokens))]
    colors2 = ["#55A868" if c else "#CCCCCC" for c in mlm_contrib]
    axes[1].bar(range(len(mlm_tokens)), [1] * len(mlm_tokens), color=colors2)
    axes[1].set_xticks(range(len(mlm_tokens)))
    axes[1].set_xticklabels(mlm_tokens)
    axes[1].set_yticks([])
    axes[1].set_title("Masked LM(BERT) — [MASK]로 가려진 위치만 loss에 기여")

    plt.suptitle('"어느 위치가 학습 신호(loss)를 만드는가" — 초록=기여함, 회색=기여 안 함',
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  학습 목적함수: Causal LM(GPT) vs Masked LM(BERT)")
    print("=" * 60)
    print(f"\n  문장: '{SENTENCE}'")

    print("\n[ 1. Causal LM(GPT) — 다음 토큰 예측 ]")
    print("-" * 40)
    causal_tokens, causal_targets, causal_loss = causal_lm_targets()

    print("\n[ 2. Masked LM(BERT) — 빈칸(마스킹) 채우기 ]")
    print("-" * 40)
    mlm_tokens, mlm_mask_positions, mlm_loss = masked_lm_targets()

    print("\n[ 3. 시각화 ]")
    print("-" * 40)
    plot_loss_contribution(causal_tokens, causal_targets, mlm_tokens, mlm_mask_positions)

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. "loss가 어디서 계산되는가"가 두 모델의 성격을 결정한다:
   - Causal LM(GPT): 모든 위치가 "바로 다음 토큰"을 맞혀야 한다 → 왼쪽 문맥만 보고 다음을
     잇는 연습을 수억 번 반복 → 자연스럽게 '생성'에 강해진다
   - Masked LM(BERT): 가려진 위치만 맞히면 된다 → 양쪽 문맥을 동시에 볼 수 있다(뒤도 이미
     보여도 되니까) → 자연스럽게 '이해/문맥 파악'에 강해진다

2. 왜 BERT는 생성이 어색하고 GPT는 빈칸 채우기가 안 되는가:
   - BERT는 애초에 "왼쪽만 보고 잇기"를 한 번도 연습한 적이 없다(항상 양쪽을 다 봤다)
   - GPT는 애초에 "미래 토큰을 보면 안 되게" 마스킹(causal mask)하고 학습해서, 뒤쪽 정보를
     활용하는 빈칸 채우기 방식 자체를 모른다

3. label = -100 컨벤션:
   - HuggingFace에서 -100은 "이 위치는 loss 계산에서 제외하라"는 신호다
   - Masked LM은 안 가려진 위치를 전부 -100으로 채워서 "가려진 곳만" 학습 신호를 만든다
   - Causal LM은 보통 이런 마스킹 없이 전체가 다 학습 신호가 된다(패딩 위치 정도만 -100 처리)

4. 이것이 왜 중요한가(실전 연결):
   - `1.openai`/`3.anthropic`에서 쓰는 모든 챗 모델은 Causal LM 계열이다(다음 토큰 예측의 연장)
   - `2.bert`에서 파인튜닝한 분류기는 Masked LM으로 사전학습된 모델 위에 분류 헤드를 얹은 것
   - "왜 GPT는 대화형이고 BERT는 분류/검색에 쓰이는가"의 답이 바로 이 학습 목적함수 차이다
""")


if __name__ == "__main__":
    main()
