"""
BERT Self-Attention 가중치 시각화
- 설치: pip install transformers torch matplotlib seaborn
"""
import os
import warnings
import torch
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModel

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def get_attention_weights(text, model_name="google-bert/bert-base-multilingual-cased"):
    """BERT에서 Attention 가중치를 추출"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)

    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    with torch.no_grad():
        outputs = model(**inputs)

    # attentions: (num_layers, batch, num_heads, seq_len, seq_len)
    attentions = outputs.attentions
    return tokens, attentions


def plot_attention_heatmap(tokens, attention, layer=0, head=0, filename="attention_heatmap.png"):
    """특정 레이어/헤드의 Attention을 히트맵으로 시각화"""
    # attention[layer]: (batch, num_heads, seq_len, seq_len)
    attn_matrix = attention[layer][0, head].numpy()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        attn_matrix,
        xticklabels=tokens,
        yticklabels=tokens,
        cmap="YlOrRd",
        annot=True,
        fmt=".2f",
        square=True,
        ax=ax,
    )
    ax.set_title(f"Self-Attention (Layer {layer}, Head {head})")
    ax.set_xlabel("Key (attended to)")
    ax.set_ylabel("Query (attending from)")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_multi_head_attention(tokens, attention, layer=0, filename="attention_multihead.png"):
    """한 레이어의 여러 Attention Head를 한 번에 시각화"""
    num_heads = attention[layer].shape[1]
    display_heads = min(num_heads, 6)  # 최대 6개 헤드만 표시

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for head in range(display_heads):
        attn_matrix = attention[layer][0, head].numpy()
        sns.heatmap(
            attn_matrix,
            xticklabels=tokens,
            yticklabels=tokens,
            cmap="YlOrRd",
            square=True,
            ax=axes[head],
            cbar=False,
        )
        axes[head].set_title(f"Head {head}")

    plt.suptitle(f"Multi-Head Attention (Layer {layer})", fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_layer_comparison(tokens, attention, filename="attention_layers.png"):
    """레이어별 Attention 패턴 변화 시각화"""
    num_layers = len(attention)
    display_layers = [0, num_layers // 4, num_layers // 2, num_layers - 1]

    fig, axes = plt.subplots(1, len(display_layers), figsize=(20, 5))

    for idx, layer in enumerate(display_layers):
        # 모든 헤드의 평균 Attention
        attn_avg = attention[layer][0].mean(dim=0).numpy()
        sns.heatmap(
            attn_avg,
            xticklabels=tokens,
            yticklabels=tokens,
            cmap="YlOrRd",
            square=True,
            ax=axes[idx],
            cbar=False,
        )
        axes[idx].set_title(f"Layer {layer} (avg)")

    plt.suptitle("Layer-wise Attention Pattern", fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def analyze_attention_patterns(tokens, attention):
    """Attention 패턴 텍스트 분석 (시각화 없이)"""
    print("\n  Attention 패턴 분석 (마지막 레이어, 전체 헤드 평균):")
    last_layer = len(attention) - 1
    attn_avg = attention[last_layer][0].mean(dim=0)  # (seq_len, seq_len)

    # 각 토큰이 가장 주목하는 토큰 출력
    for i, token in enumerate(tokens):
        top_indices = attn_avg[i].topk(3).indices.tolist()
        top_values = attn_avg[i].topk(3).values.tolist()
        top_tokens = [(tokens[j], f"{v:.3f}") for j, v in zip(top_indices, top_values)]
        print(f"    {token:>15} → {top_tokens}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  BERT Self-Attention 시각화")
    print("=" * 60)

    # ── 예제 1: 영어 문장 ──
    print("\n[ 1. 영어 문장 ]")
    print("-" * 40)

    en_text = "The cat sat on the mat."
    print(f"  입력: {en_text}")

    tokens_en, attn_en = get_attention_weights(en_text)
    print(f"  토큰: {tokens_en}")
    print(f"  레이어 수: {len(attn_en)}, 헤드 수: {attn_en[0].shape[1]}")

    plot_attention_heatmap(tokens_en, attn_en, layer=0, head=0, filename="results/1.attention_en_L0H0.png")
    plot_multi_head_attention(tokens_en, attn_en, layer=0, filename="results/1.attention_en_multihead.png")
    analyze_attention_patterns(tokens_en, attn_en)

    # ── 예제 2: 한국어 문장 ──
    print("\n[ 2. 한국어 문장 ]")
    print("-" * 40)

    ko_text = "인공지능이 세상을 바꾸고 있다."
    print(f"  입력: {ko_text}")

    tokens_ko, attn_ko = get_attention_weights(ko_text)
    print(f"  토큰: {tokens_ko}")

    plot_attention_heatmap(tokens_ko, attn_ko, layer=0, head=0, filename="results/1.attention_ko_L0H0.png")
    analyze_attention_patterns(tokens_ko, attn_ko)

    # ── 예제 3: 레이어별 변화 ──
    print("\n[ 3. 레이어별 Attention 변화 ]")
    print("-" * 40)

    plot_layer_comparison(tokens_en, attn_en, filename="results/1.attention_layers.png")
    print("  초기 레이어: 인접 단어에 주목 (문법적 관계)")
    print("  후기 레이어: 의미적으로 관련된 단어에 주목 (의미적 관계)")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. Self-Attention 메커니즘:
   - Query, Key, Value 행렬로 토큰 간 관계 계산
   - Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V
   - 모든 토큰 쌍의 관계를 동시에 계산 (병렬 처리)

2. Multi-Head Attention:
   - 여러 헤드가 서로 다른 관점에서 주목
   - Head 0: 문법적 관계 (주어-동사)
   - Head 1: 의미적 관계 (명사-형용사)
   - Head 2: 위치적 관계 (인접 토큰)

3. 레이어별 패턴:
   - 초기 레이어: 인접 토큰, [CLS], [SEP]에 주목
   - 중간 레이어: 문법적 구조 포착
   - 후기 레이어: 의미적 관계, 태스크 관련 패턴

4. 한국어 Attention 특성:
   - 서브워드 토큰 간 강한 어텐션 (같은 단어의 조각들)
   - 조사가 명사에 강하게 주목
   - [CLS] 토큰이 문장 전체 의미를 압축
""")


if __name__ == "__main__":
    main()
