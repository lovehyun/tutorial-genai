"""
Q, K, V 행렬 내부 동작 시각화 — Attention 계산 과정을 단계별로 분해
- 설치: pip install transformers torch matplotlib seaborn numpy
"""
import os
import warnings
import torch
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModel

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "google-bert/bert-base-multilingual-cased"


def extract_qkv(text, model_name=MODEL_NAME, layer=0, head=0):
    """BERT의 특정 레이어/헤드에서 Q, K, V 행렬을 추출"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(
        model_name, output_attentions=True, output_hidden_states=True)

    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    with torch.no_grad():
        outputs = model(**inputs)

    # hidden_states[0] = 임베딩 출력, hidden_states[N] = N번째 레이어 출력
    # 레이어 N의 입력 = hidden_states[N] (0이면 임베딩, 아니면 이전 레이어 출력)
    attn_layer = model.encoder.layer[layer].attention.self
    embed_output = outputs.hidden_states[layer]

    # Q, K, V 선형 변환
    Q = attn_layer.query(embed_output)  # (1, seq_len, hidden_size)
    K = attn_layer.key(embed_output)
    V = attn_layer.value(embed_output)

    # multi-head 분리: (batch, seq_len, num_heads, head_dim) → 특정 head 추출
    num_heads = attn_layer.num_attention_heads
    head_dim = Q.shape[-1] // num_heads

    Q = Q.view(1, -1, num_heads, head_dim)[0, :, head, :]  # (seq_len, head_dim)
    K = K.view(1, -1, num_heads, head_dim)[0, :, head, :]
    V = V.view(1, -1, num_heads, head_dim)[0, :, head, :]

    # Attention 계산 단계
    # 1) QK^T / sqrt(d_k)
    scale = head_dim ** 0.5
    qk_scores = torch.matmul(Q, K.transpose(0, 1)) / scale  # (seq_len, seq_len)

    # 2) softmax
    attn_weights = torch.softmax(qk_scores, dim=-1)

    # 3) Attention output = weights × V
    attn_output = torch.matmul(attn_weights, V)  # (seq_len, head_dim)

    return {
        'tokens': tokens,
        'Q': Q.detach().numpy(),
        'K': K.detach().numpy(),
        'V': V.detach().numpy(),
        'qk_scores': qk_scores.detach().numpy(),
        'attn_weights': attn_weights.detach().numpy(),
        'attn_output': attn_output.detach().numpy(),
        'head_dim': head_dim,
        'scale': scale,
    }


def plot_qkv_matrices(data, filename="2.qkv_matrices.png"):
    """Q, K, V 행렬을 나란히 히트맵으로 시각화"""
    tokens = data['tokens']
    dims_to_show = min(16, data['head_dim'])  # 처음 16차원만

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    matrices = [('Query (Q)', data['Q']), ('Key (K)', data['K']), ('Value (V)', data['V'])]

    for ax, (title, matrix) in zip(axes, matrices):
        sns.heatmap(
            matrix[:, :dims_to_show],
            yticklabels=tokens,
            cmap="RdBu_r",
            center=0,
            ax=ax,
            cbar_kws={'shrink': 0.8},
        )
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_xlabel(f'Dimension (first {dims_to_show} of {data["head_dim"]})')
        ax.set_ylabel('Tokens')

    plt.suptitle('Q, K, V Matrices — Linear Projections of Input Embeddings\n'
                 'Each token is transformed into Query, Key, Value vectors',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_attention_steps(data, filename="2.qkv_attention_steps.png"):
    """Attention 계산 4단계를 순서대로 시각화"""
    tokens = data['tokens']

    fig, axes = plt.subplots(2, 2, figsize=(16, 14))

    # Step 1: QK^T (스케일링 전)
    raw_qk = data['qk_scores'] * data['scale']  # 스케일링 되돌리기
    sns.heatmap(raw_qk, xticklabels=tokens, yticklabels=tokens,
                cmap="RdBu_r", center=0, annot=True, fmt=".1f",
                square=True, ax=axes[0, 0])
    axes[0, 0].set_title('Step 1: QK$^T$ (raw dot product)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Key tokens')
    axes[0, 0].set_ylabel('Query tokens')

    # Step 2: QK^T / sqrt(d_k) (스케일링 후)
    sns.heatmap(data['qk_scores'], xticklabels=tokens, yticklabels=tokens,
                cmap="RdBu_r", center=0, annot=True, fmt=".1f",
                square=True, ax=axes[0, 1])
    axes[0, 1].set_title(f'Step 2: QK$^T$ / $\\sqrt{{d_k}}$  (d_k={data["head_dim"]})',
                         fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Key tokens')
    axes[0, 1].set_ylabel('Query tokens')

    # Step 3: softmax (Attention 가중치)
    sns.heatmap(data['attn_weights'], xticklabels=tokens, yticklabels=tokens,
                cmap="YlOrRd", annot=True, fmt=".2f",
                square=True, ax=axes[1, 0], vmin=0, vmax=1)
    axes[1, 0].set_title('Step 3: softmax → Attention Weights', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Key tokens (attended to)')
    axes[1, 0].set_ylabel('Query tokens (attending from)')

    # Step 4: Attention Output (weights × V)
    dims_to_show = min(16, data['head_dim'])
    sns.heatmap(data['attn_output'][:, :dims_to_show], yticklabels=tokens,
                cmap="RdBu_r", center=0, ax=axes[1, 1])
    axes[1, 1].set_title('Step 4: Attention Output (weights × V)', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel(f'Dimension (first {dims_to_show})')
    axes[1, 1].set_ylabel('Tokens')

    plt.suptitle('Self-Attention Step by Step: Q×K$^T$ → scale → softmax → ×V',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_softmax_effect(data, filename="2.qkv_softmax_effect.png"):
    """softmax 전/후 비교 — 확률 분포로 변환되는 과정"""
    tokens = data['tokens']
    seq_len = len(tokens)

    # 대표 토큰 3개 선택 (첫 번째, 중간, 마지막 실질 토큰)
    sample_indices = [0, seq_len // 2, seq_len - 2]  # [CLS], 중간, 마지막 단어

    fig, axes = plt.subplots(len(sample_indices), 2, figsize=(16, 4 * len(sample_indices)))

    for row, idx in enumerate(sample_indices):
        # softmax 전 (raw scores)
        raw = data['qk_scores'][idx]
        axes[row, 0].bar(range(seq_len), raw, color='#4C72B0', alpha=0.8)
        axes[row, 0].set_title(f'Before softmax: "{tokens[idx]}"', fontsize=11, fontweight='bold')
        axes[row, 0].set_xticks(range(seq_len))
        axes[row, 0].set_xticklabels(tokens, rotation=45, ha='right', fontsize=8)
        axes[row, 0].set_ylabel('Raw score')
        axes[row, 0].axhline(y=0, color='gray', linewidth=0.5)

        # softmax 후 (확률)
        probs = data['attn_weights'][idx]
        colors = ['#C44E52' if p == max(probs) else '#55A868' for p in probs]
        axes[row, 1].bar(range(seq_len), probs, color=colors, alpha=0.8)
        axes[row, 1].set_title(f'After softmax: "{tokens[idx]}"', fontsize=11, fontweight='bold')
        axes[row, 1].set_xticks(range(seq_len))
        axes[row, 1].set_xticklabels(tokens, rotation=45, ha='right', fontsize=8)
        axes[row, 1].set_ylabel('Probability')
        axes[row, 1].set_ylim(0, 1)
        # sum=1 표시
        axes[row, 1].text(0.98, 0.95, f'sum={sum(probs):.2f}',
                          transform=axes[row, 1].transAxes, ha='right', va='top',
                          fontsize=10, color='gray')

    plt.suptitle('Softmax Effect — Raw Scores → Probability Distribution\n'
                 'Softmax normalizes scores so they sum to 1.0',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_qk_similarity(data, filename="2.qkv_qk_similarity.png"):
    """Q와 K 벡터 간 유사도를 시각적으로 비교 — 왜 특정 토큰에 주목하는지"""
    tokens = data['tokens']
    Q, K = data['Q'], data['K']
    seq_len = len(tokens)

    # 대표 query 토큰 선택
    query_idx = 1  # 보통 첫 번째 실질 토큰

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1) Query 벡터
    dims = min(32, data['head_dim'])
    q_vec = Q[query_idx, :dims]
    colors_q = ['#4C72B0' if v >= 0 else '#C44E52' for v in q_vec]
    axes[0].bar(range(dims), q_vec, color=colors_q, width=0.8)
    axes[0].set_title(f'Query vector: "{tokens[query_idx]}"', fontsize=11, fontweight='bold')
    axes[0].set_xlabel(f'Dimension (first {dims})')
    axes[0].set_ylabel('Value')
    axes[0].axhline(y=0, color='black', linewidth=0.5)

    # 2) 각 Key 벡터와의 내적
    dot_products = data['qk_scores'][query_idx]
    colors_dp = ['#C44E52' if dp == max(dot_products) else '#4C72B0' for dp in dot_products]
    axes[1].barh(range(seq_len), dot_products, color=colors_dp, height=0.6)
    axes[1].set_yticks(range(seq_len))
    axes[1].set_yticklabels(tokens, fontsize=9)
    axes[1].set_title(f'Q·K$^T$ scores for "{tokens[query_idx]}"', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Dot product / sqrt(d_k)')
    axes[1].axvline(x=0, color='gray', linewidth=0.5)
    axes[1].invert_yaxis()

    # 3) softmax 결과 (최종 attention)
    attn = data['attn_weights'][query_idx]
    colors_a = ['#C44E52' if a == max(attn) else '#55A868' for a in attn]
    axes[2].barh(range(seq_len), attn, color=colors_a, height=0.6)
    axes[2].set_yticks(range(seq_len))
    axes[2].set_yticklabels(tokens, fontsize=9)
    axes[2].set_title(f'Attention weights for "{tokens[query_idx]}"', fontsize=11, fontweight='bold')
    axes[2].set_xlabel('Probability')
    axes[2].set_xlim(0, 1)
    axes[2].invert_yaxis()

    plt.suptitle(f'Why does "{tokens[query_idx]}" attend to certain tokens?\n'
                 f'Query vector → dot product with Keys → softmax → attention weights',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  Q, K, V 내부 동작 시각화")
    print("=" * 60)

    text = "The cat sat on the mat."
    layer, head = 0, 0

    # ── 1. QKV 추출 ──
    print(f"\n  모델: {MODEL_NAME}")
    print(f"  입력: {text}")
    print(f"  레이어: {layer}, 헤드: {head}")

    print("\n[ 1. Q, K, V 행렬 추출 ]")
    print("-" * 40)
    data = extract_qkv(text, layer=layer, head=head)
    print(f"  토큰: {data['tokens']}")
    print(f"  Q shape: {data['Q'].shape} (seq_len × head_dim)")
    print(f"  K shape: {data['K'].shape}")
    print(f"  V shape: {data['V'].shape}")
    print(f"  head_dim: {data['head_dim']}, scale: {data['scale']:.2f}")

    # ── 2. QKV 행렬 시각화 ──
    print("\n[ 2. Q, K, V 행렬 시각화 ]")
    print("-" * 40)
    plot_qkv_matrices(data, "results/2.qkv_matrices.png")

    # ── 3. Attention 단계별 시각화 ──
    print("\n[ 3. Attention 계산 4단계 ]")
    print("-" * 40)
    print("  Step 1: QK^T (토큰 간 내적 = 유사도)")
    print("  Step 2: / sqrt(d_k) (스케일링 → 그래디언트 안정화)")
    print("  Step 3: softmax (확률 분포로 변환)")
    print("  Step 4: × V (가중합 → 최종 출력)")
    plot_attention_steps(data, "results/2.qkv_attention_steps.png")

    # ── 4. softmax 전/후 비교 ──
    print("\n[ 4. softmax 전/후 비교 ]")
    print("-" * 40)
    plot_softmax_effect(data, "results/2.qkv_softmax_effect.png")

    # ── 5. Q-K 유사도 분석 ──
    print("\n[ 5. Q-K 유사도 분석 ]")
    print("-" * 40)
    plot_qk_similarity(data, "results/2.qkv_qk_similarity.png")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. Q, K, V의 역할:
   - Query(Q): "나는 어떤 정보를 찾고 있는가?" — 질문 역할
   - Key(K): "나는 어떤 정보를 가지고 있는가?" — 색인 역할
   - Value(V): "내가 전달할 실제 정보" — 콘텐츠 역할
   - 같은 입력에서 서로 다른 선형 변환으로 생성

2. Attention 계산 과정:
   - QK^T: 모든 Query-Key 쌍의 내적 → 유사도 행렬
   - / sqrt(d_k): 차원이 클수록 내적이 커지므로 스케일링
   - softmax: 음수~양수 점수를 0~1 확률로 변환 (합=1)
   - × V: 확률로 Value를 가중평균 → 문맥 반영된 새 표현

3. 왜 QKV를 분리하는가:
   - Q만으로 "무엇을 찾을지" 결정
   - K만으로 "무엇이 관련있는지" 판단
   - V만으로 "어떤 정보를 전달할지" 결정
   - 분리함으로써 "찾는 것"과 "전달하는 것"이 독립적

4. Multi-Head의 의미:
   - 각 Head는 다른 QKV 가중치 → 다른 관점
   - Head 0: 문법적 관계, Head 1: 의미적 관계 등
   - 여러 Head의 출력을 concat하여 풍부한 표현 생성
""")


if __name__ == "__main__":
    main()
