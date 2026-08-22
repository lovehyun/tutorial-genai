"""
임베딩 벡터 시각화 — 벡터가 실제 숫자 배열로 어떻게 생겼는지 + 유사/비유사 비교
- 설치: pip install sentence-transformers matplotlib seaborn numpy scikit-learn
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# 유사한 쌍 + 비유사한 쌍
SENTENCE_PAIRS = [
    ("인공지능이 세상을 바꾸고 있다.", "AI가 세계를 변화시키고 있다.", "similar"),
    ("오늘 날씨가 정말 좋다.", "맛있는 피자를 먹고 싶다.", "different"),
    ("파이썬은 배우기 쉬운 프로그래밍 언어다.", "Python은 초보자에게 좋은 코딩 언어다.", "similar"),
    ("주말에 산에 등산을 갔다.", "양자역학은 미시세계를 설명한다.", "different"),
]


def plot_embedding_vector(sentence, embedding, filename="2.embedding_vector.png"):
    """임베딩 벡터의 처음 50차원을 바 차트로 시각화 (양수=파랑, 음수=빨강)"""
    dims = 50
    values = embedding[:dims]
    colors = ['#4C72B0' if v >= 0 else '#C44E52' for v in values]

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.bar(range(dims), values, color=colors, width=0.8, edgecolor='none')
    ax.set_xlabel('Dimension')
    ax.set_ylabel('Value')
    ax.set_title(f'Embedding Vector (first {dims} of {len(embedding)} dims)\n"{sentence}"',
                 fontsize=12, fontweight='bold')
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlim(-0.5, dims - 0.5)
    ax.grid(axis='y', alpha=0.3)

    # 통계 정보 표시
    stats_text = (f'Total dims: {len(embedding)}  |  '
                  f'Mean: {embedding.mean():.4f}  |  '
                  f'Std: {embedding.std():.4f}  |  '
                  f'Min: {embedding.min():.4f}  |  '
                  f'Max: {embedding.max():.4f}')
    ax.text(0.5, -0.15, stats_text, ha='center', va='top',
            transform=ax.transAxes, fontsize=9, color='gray')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_embedding_comparison(sent1, sent2, emb1, emb2, similarity, filename):
    """두 벡터를 나란히 + 차이 벡터 + 코사인 유사도 표시"""
    dims = 50
    v1, v2 = emb1[:dims], emb2[:dims]
    diff = v1 - v2

    fig, axes = plt.subplots(3, 1, figsize=(14, 9))

    # 벡터 1
    colors1 = ['#4C72B0' if v >= 0 else '#C44E52' for v in v1]
    axes[0].bar(range(dims), v1, color=colors1, width=0.8)
    axes[0].set_title(f'Sentence A: "{sent1}"', fontsize=10)
    axes[0].set_ylabel('Value')
    axes[0].axhline(y=0, color='black', linewidth=0.5)
    axes[0].set_xlim(-0.5, dims - 0.5)

    # 벡터 2
    colors2 = ['#4C72B0' if v >= 0 else '#C44E52' for v in v2]
    axes[1].bar(range(dims), v2, color=colors2, width=0.8)
    axes[1].set_title(f'Sentence B: "{sent2}"', fontsize=10)
    axes[1].set_ylabel('Value')
    axes[1].axhline(y=0, color='black', linewidth=0.5)
    axes[1].set_xlim(-0.5, dims - 0.5)

    # 차이 벡터
    colors_d = ['#55A868' if abs(v) < 0.1 else '#DD8452' for v in diff]
    axes[2].bar(range(dims), diff, color=colors_d, width=0.8)
    axes[2].set_title(f'Difference (A - B)  |  Cosine Similarity: {similarity:.4f}', fontsize=10)
    axes[2].set_xlabel('Dimension')
    axes[2].set_ylabel('Diff')
    axes[2].axhline(y=0, color='black', linewidth=0.5)
    axes[2].set_xlim(-0.5, dims - 0.5)

    plt.suptitle(f'Embedding Vector Comparison (first {dims} dims)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_similarity_bars(pairs, similarities, filename="2.similarity_bars.png"):
    """문장 쌍별 유사도를 수평 바로 시각화 (빨강↔초록)"""
    n = len(pairs)
    fig, ax = plt.subplots(figsize=(12, max(4, n * 1.2)))

    # 유사도에 따른 색상 (빨강 → 노랑 → 초록)
    cmap = plt.cm.RdYlGn
    colors = [cmap(s) for s in similarities]

    y_pos = range(n)
    bars = ax.barh(y_pos, similarities, color=colors, height=0.6, edgecolor='white')

    # 라벨 표시
    labels = []
    for s1, s2, _ in pairs:
        s1_short = s1 if len(s1) <= 20 else s1[:17] + '...'
        s2_short = s2 if len(s2) <= 20 else s2[:17] + '...'
        labels.append(f'{s1_short}\nvs  {s2_short}')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Cosine Similarity')
    ax.set_title('Sentence Pair Similarity', fontsize=13, fontweight='bold')
    ax.set_xlim(0, 1.0)
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5, label='threshold=0.5')

    # 바 끝에 숫자 표시
    for bar, sim in zip(bars, similarities):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f'{sim:.3f}', va='center', fontsize=10, fontweight='bold')

    ax.legend()
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  임베딩 벡터 시각화")
    print("=" * 60)

    # 모델 로드
    print(f"\n  모델 로드: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # ── 1. 단일 벡터 시각화 ──
    print("\n[ 1. 임베딩 벡터 구조 ]")
    print("-" * 40)

    sample = "인공지능이 세상을 바꾸고 있다."
    emb = model.encode(sample)
    print(f"  문장: {sample}")
    print(f"  벡터 차원: {emb.shape[0]}")
    print(f"  처음 10개 값: {emb[:10].round(4)}")

    plot_embedding_vector(sample, emb, "results/2.embedding_vector.png")

    # ── 2. 유사/비유사 문장 비교 ──
    print("\n[ 2. 문장 쌍 비교 ]")
    print("-" * 40)

    all_sims = []
    for i, (s1, s2, rel) in enumerate(SENTENCE_PAIRS):
        e1, e2 = model.encode(s1), model.encode(s2)
        sim = cosine_similarity([e1], [e2])[0][0]
        all_sims.append(sim)
        print(f"  쌍 {i+1} ({rel}): {sim:.4f}")
        print(f"    A: {s1}")
        print(f"    B: {s2}")

        # 유사 쌍과 비유사 쌍 각각 시각화
        if i == 0:
            plot_embedding_comparison(s1, s2, e1, e2, sim, "results/2.embedding_compare_similar.png")
        elif i == 1:
            plot_embedding_comparison(s1, s2, e1, e2, sim, "results/2.embedding_compare_different.png")

    # ── 3. 유사도 바 차트 ──
    print("\n[ 3. 유사도 바 차트 ]")
    print("-" * 40)
    plot_similarity_bars(SENTENCE_PAIRS, all_sims, "results/2.similarity_bars.png")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 임베딩 벡터:
   - 문장을 고정 길이(384차원) 숫자 배열로 변환
   - 각 차원은 문장의 의미적 특성을 인코딩
   - 양수/음수 값이 혼재 — 특정 의미 방향을 나타냄

2. 코사인 유사도:
   - 두 벡터의 방향 유사성 측정 (0~1, 높을수록 유사)
   - "AI가 세상을 바꾸다" ≈ "인공지능이 세계를 변화시키다" → 높은 유사도
   - "날씨가 좋다" vs "피자를 먹고 싶다" → 낮은 유사도

3. 벡터 차이:
   - 유사한 문장: 차이 벡터의 값이 작음 (대부분 0에 가까움)
   - 비유사 문장: 차이 벡터의 값이 큼 (많은 차원에서 차이)

4. 다국어 임베딩:
   - paraphrase-multilingual-MiniLM: 50+ 언어 지원
   - 한국어 ↔ 영어 교차 언어 유사도도 포착
""")


if __name__ == "__main__":
    main()
