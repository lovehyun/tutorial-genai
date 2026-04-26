"""
토큰화 과정 시각화 — 서브워드 분할을 색상 바 차트로 비교
- 설치: pip install transformers sentencepiece matplotlib
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from transformers import AutoTokenizer

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 토크나이저 스펙 (모델명, 표시 레이블)
TOKENIZER_SPECS = [
    ("google-bert/bert-base-multilingual-cased", "WordPiece (BERT)"),
    ("openai-community/gpt2", "BPE (GPT-2)"),
    ("google-t5/t5-base", "SentencePiece (T5)"),
]

SAMPLE_SENTENCES = [
    "인공지능이 세상을 바꾸고 있다.",
    "GPT-4는 OpenAI가 만든 대규모 언어모델입니다.",
    "자연어 처리는 컴퓨터가 사람의 언어를 이해하는 기술이다.",
]

# 토큰별 색상 팔레트
TOKEN_COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]


def tokenize_with_info(text, model_name):
    """토크나이저로 텍스트를 분할하고 토큰 목록과 ID를 반환"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    # 전체 복원 텍스트 (BPE 바이트 토큰 그룹을 한글로 복원)
    decoded_text = tokenizer.decode(token_ids)
    return tokens, token_ids, decoded_text


def plot_token_comparison(text, tokenizer_specs, filename="1.tokenize_comparison.png"):
    """1개 문장에 대해 3개 토크나이저 결과를 수평 세그먼트 바로 시각화"""
    fig, axes = plt.subplots(len(tokenizer_specs), 1, figsize=(14, 2.5 * len(tokenizer_specs)))
    if len(tokenizer_specs) == 1:
        axes = [axes]

    fig.suptitle(f'Token Segmentation Comparison\n"{text}"', fontsize=13, fontweight='bold')

    for ax_idx, (model_name, label) in enumerate(tokenizer_specs):
        ax = axes[ax_idx]
        tokens, token_ids, decoded_text = tokenize_with_info(text, model_name)
        n_tokens = len(tokens)

        # 각 토큰을 색상 블록으로 배치
        for i, token in enumerate(tokens):
            color = TOKEN_COLORS[i % len(TOKEN_COLORS)]
            ax.barh(0, 1, left=i, height=0.6, color=color, edgecolor='white', linewidth=1)
            # 토큰 텍스트 표시 (서브워드 접두사 제거)
            display_text = token.replace('##', '').replace('▁', '_').replace('Ġ', ' ')
            # 토큰 수가 많으면 폰트 축소
            fsize = 6 if n_tokens > 25 else 8
            ax.text(i + 0.5, 0, display_text, ha='center', va='center',
                    fontsize=fsize, fontweight='bold', color='white')

        ax.set_xlim(0, max(n_tokens, 1))
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel(f'{label}  —  {n_tokens} tokens')
        ax.set_xticks(range(n_tokens))
        ax.set_xticklabels([f'{i}' for i in range(n_tokens)], fontsize=7)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_token_count_comparison(sentences, tokenizer_specs, filename="1.tokenize_counts.png"):
    """여러 문장의 토큰 수를 그룹 바 차트로 비교"""
    n_sentences = len(sentences)
    n_tokenizers = len(tokenizer_specs)
    bar_width = 0.25
    x = np.arange(n_sentences)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#4C72B0', '#DD8452', '#55A868']

    for t_idx, (model_name, label) in enumerate(tokenizer_specs):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        counts = [len(tokenizer.tokenize(s)) for s in sentences]
        bars = ax.bar(x + t_idx * bar_width, counts, bar_width,
                      label=label, color=colors[t_idx], edgecolor='white')
        # 바 위에 숫자 표시
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel('Sentences')
    ax.set_ylabel('Token Count')
    ax.set_title('Token Count by Tokenizer Algorithm', fontsize=13, fontweight='bold')
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels([f'Sent {i+1}' for i in range(n_sentences)], fontsize=10)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # 문장 텍스트를 하단에 표시
    text_y = -0.18
    for i, sent in enumerate(sentences):
        display = sent if len(sent) <= 35 else sent[:32] + '...'
        ax.text(i + bar_width, text_y, display,
                ha='center', va='top', fontsize=8, transform=ax.get_xaxis_transform())

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  토큰화 과정 시각화")
    print("=" * 60)

    # ── 1. 토큰 세그먼트 비교 ──
    print("\n[ 1. 토큰 세그먼트 비교 ]")
    print("-" * 40)
    for i, sent in enumerate(SAMPLE_SENTENCES):
        print(f"\n  문장 {i+1}: {sent}")
        for model_name, label in TOKENIZER_SPECS:
            tokens, ids, decoded_text = tokenize_with_info(sent, model_name)
            print(f"    {label}: {len(tokens)}개 → {tokens}")
            print(f"      복원: {decoded_text}")

    # 첫 번째 문장으로 세그먼트 비교 시각화
    plot_token_comparison(SAMPLE_SENTENCES[0], TOKENIZER_SPECS, "results/1.tokenize_comparison.png")

    # ── 2. 토큰 수 비교 ──
    print("\n[ 2. 토큰 수 비교 ]")
    print("-" * 40)
    plot_token_count_comparison(SAMPLE_SENTENCES, TOKENIZER_SPECS, "results/1.tokenize_counts.png")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 서브워드 토크나이징:
   - 같은 문장이라도 토크나이저에 따라 분할 방식이 다름
   - WordPiece(BERT): ##접두사로 서브워드 표시
   - BPE(GPT-2): 바이트 단위 병합, 영어에 최적화
   - SentencePiece(T5): 공백도 토큰에 포함 (언어 무관)

2. 한국어 토큰 효율성:
   - 영어 중심 토크나이저는 한국어를 잘게 쪼갬
   - 토큰 수 = API 비용이므로 효율적 토크나이저 선택이 중요

3. 토큰화가 중요한 이유:
   - 모델이 보는 것은 "단어"가 아니라 "토큰"
   - 토큰 단위가 임베딩 벡터의 기본 단위
   - 다음 단계: 토큰 → 벡터 (임베딩)로 변환
""")


if __name__ == "__main__":
    main()
