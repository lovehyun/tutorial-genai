"""
샘플링/디코딩 전략 시각화 — "다음 토큰 확률"을 실제로 눈으로 본다
- 설치: pip install transformers torch matplotlib numpy

31.local/1.transformers/4.1_decoding_strategies.py 가 greedy/beam/temperature/top-k/top-p를
텍스트 출력으로 비교했다면, 여기는 **그 각각이 확률 분포를 어떻게 바꾸는지**를 그림으로 본다 —
"temperature를 올리면 왜 더 무작위스러워지는가"를 숫자·그래프로 직접 확인한다.
"""
import os
import warnings
import numpy as np
import torch
import matplotlib
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModelForCausalLM

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "gpt2"
PROMPT = "The capital of France is"


def get_next_token_probs(prompt: str, temperature: float = 1.0):
    """다음 토큰 확률 분포 — temperature로 나눈 뒤 softmax(온도가 낮을수록 뾰족해진다)."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()

    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits[0, -1, :]

    scaled = logits / temperature
    probs = torch.softmax(scaled, dim=-1)
    return probs, tokenizer


def plot_temperature_effect(filename="results/1.temperature_effect.png"):
    """같은 분포를 temperature 3가지로 리스케일 — 낮을수록 뾰족, 높을수록 평평해진다."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    inputs = tokenizer(PROMPT, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits[0, -1, :]

    temperatures = [0.5, 1.0, 2.0]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 기준(T=1.0)에서 상위 12개 토큰을 고정하고, 그 '같은 토큰들'이 온도에 따라 어떻게 바뀌는지 비교
    base_probs = torch.softmax(logits, dim=-1)
    top_idx = torch.topk(base_probs, 12).indices

    for ax, T in zip(axes, temperatures):
        probs = torch.softmax(logits / T, dim=-1)
        values = probs[top_idx].detach().numpy()
        labels = [tokenizer.decode([i]).strip() or "·" for i in top_idx]
        colors = ["#C44E52" if i == 0 else "#4C72B0" for i in range(len(labels))]
        ax.bar(range(len(labels)), values, color=colors)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_ylim(0, 1)
        ax.set_title(f"temperature = {T}")
        ax.set_ylabel("확률")

    plt.suptitle(f'"{PROMPT} ___" 의 다음 토큰 확률 — temperature 효과\n'
                 "낮을수록(0.5) 1등에 확률이 몰리고, 높을수록(2.0) 고르게 퍼진다",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def plot_topk_topp(filename="results/2.topk_topp.png"):
    """top-k / top-p가 실제로 '어디서 잘라내는지'를 누적확률 그래프 위에 표시."""
    probs, tokenizer = get_next_token_probs(PROMPT, temperature=1.0)
    sorted_probs_full, sorted_idx_full = torch.sort(probs, descending=True)
    cumulative_full = np.cumsum(sorted_probs_full.detach().numpy())

    # [관전 포인트] p=0.9는 이 프롬프트에서 순위 1500번대까지 가야 도달한다(아래 출력 참고) —
    #   GPT-2(base, 소형)가 이 문장의 다음 단어를 굉장히 불확실하게 본다는 뜻이다. 그래서
    #   그래프에서는 실제로 컷오프가 눈에 보이는 더 낮은 p=0.5를 쓴다.
    p = 0.5
    cutoff_rank_p90 = int(np.searchsorted(cumulative_full, 0.9)) + 1
    cutoff_rank_p = int(np.searchsorted(cumulative_full, p)) + 1
    print(f"  참고: top-p=0.9 컷오프는 순위 {cutoff_rank_p90}위에서야 도달함(분포가 매우 평평함)")
    print(f"        그래프에는 컷오프가 눈에 보이는 top-p={p}(순위 {cutoff_rank_p}위)를 표시함")

    top_n = max(20, cutoff_rank_p + 5)
    values = sorted_probs_full[:top_n].detach().numpy()
    labels = [tokenizer.decode([i]).strip() or "·" for i in sorted_idx_full[:top_n]]
    cumulative = cumulative_full[:top_n]

    fig, axes = plt.subplots(1, 2, figsize=(max(16, top_n * 0.5), 5))

    # 왼쪽: top-k=5 컷오프 — 확률 순으로 정렬된 막대 + 살아남는/잘리는 색 구분(top 20만 표시)
    k = 5
    colors_k = ["#55A868" if i < k else "#CCCCCC" for i in range(20)]
    axes[0].bar(range(20), values[:20], color=colors_k)
    axes[0].axvline(x=k - 0.5, color="red", linestyle="--", label=f"top-k={k} 컷오프")
    axes[0].set_xticks(range(20))
    axes[0].set_xticklabels(labels[:20], rotation=45, ha="right")
    axes[0].set_ylabel("확률")
    axes[0].set_title(f"Top-k (k={k}) — 순위로 자른다")
    axes[0].legend()

    # 오른쪽: top-p 컷오프 — 누적확률 선 + 컷오프 지점이 실제로 보이도록 top_n을 넉넉히 잡음
    cutoff_idx = cutoff_rank_p - 1
    colors_p = ["#55A868" if i <= cutoff_idx else "#CCCCCC" for i in range(top_n)]
    ax2 = axes[1]
    ax2.bar(range(top_n), values, color=colors_p)
    ax2b = ax2.twinx()
    ax2b.plot(range(top_n), cumulative, color="darkred", marker="o", markersize=2, label="누적확률")
    ax2b.axhline(y=p, color="red", linestyle="--", label=f"top-p={p}")
    ax2.set_xticks(range(top_n))
    ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    ax2.set_ylabel("확률")
    ax2b.set_ylabel("누적 확률")
    ax2b.set_ylim(0, 1.05)
    ax2.set_title(f"Top-p / nucleus (p={p}) — 누적확률로 자른다 (컷오프: 순위 {cutoff_rank_p}위)")
    ax2b.legend(loc="lower right")

    plt.suptitle(f'"{PROMPT} ___" 다음 토큰 후보 — top-k vs top-p\n'
                 f"(참고: 이 분포는 매우 평평해서 top-p=0.9는 순위 {cutoff_rank_p90}위까지 가야 한다 — "
                 f"소형 모델의 낮은 확신도)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def demonstrate_repeated_sampling():
    """같은 분포에서 여러 번 샘플링 — greedy는 항상 같고, 샘플링은 매번 달라진다."""
    probs, tokenizer = get_next_token_probs(PROMPT, temperature=1.0)

    greedy_choices = [tokenizer.decode([torch.argmax(probs).item()]).strip() for _ in range(5)]
    torch.manual_seed(0)
    sampled_choices = [tokenizer.decode([torch.multinomial(probs, 1).item()]).strip() for _ in range(5)]

    print(f"  greedy 5회 반복:   {greedy_choices}  (항상 동일)")
    print(f"  sampling 5회 반복: {sampled_choices}  (매번 다를 수 있음)")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  샘플링/디코딩 전략 시각화")
    print("=" * 60)
    print(f"\n  모델: {MODEL_NAME}, 프롬프트: '{PROMPT}'")

    print("\n[ 1. greedy vs sampling 반복 — 재현성 차이 ]")
    print("-" * 40)
    demonstrate_repeated_sampling()

    print("\n[ 2. temperature가 분포를 어떻게 바꾸는가 ]")
    print("-" * 40)
    plot_temperature_effect()

    print("\n[ 3. top-k vs top-p — 어디서 잘라내는가 ]")
    print("-" * 40)
    plot_topk_topp()

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 모든 디코딩 전략은 "같은 확률 분포"에서 출발한다:
   - 모델은 매 스텝 어휘 전체에 대한 확률 분포 하나를 낸다(9.decoding_strategies의 그림들 참고)
   - "어떻게 그 분포에서 하나를 고르나"만 다를 뿐, 분포 자체는 전략과 무관하게 똑같다

2. temperature = 분포를 재조정하는 다이얼:
   - logits를 temperature로 나눈 뒤 softmax → 낮으면(<1) 뾰족해져서 1등에 쏠리고,
     높으면(>1) 평평해져서 다양한 선택지에 확률이 고르게 퍼진다
   - temperature=0에 가까우면 사실상 greedy와 같아진다

3. top-k와 top-p는 "말이 안 되는 꼬리"를 자르는 두 가지 방법:
   - top-k: 순위로 자른다(상위 k개만 남김) — 항상 같은 개수
   - top-p(nucleus): 누적 확률로 자른다(확률 합이 p가 될 때까지) — 분포가 뾰족하면 적은 수,
     평평하면 많은 수의 후보가 남는다 → 상황에 따라 유연하게 후보 수가 달라진다는 게 장점

4. greedy/beam은 확률적이지 않다(=재현 가능), sampling 계열은 확률적이다(=매번 다를 수 있음):
   - 정확도가 중요한 작업(분류·요약 사실 확인)은 greedy/beam
   - 다양성이 중요한 작업(스토리·아이디어 생성)은 sampling + temperature/top-k/top-p
""")


if __name__ == "__main__":
    main()
