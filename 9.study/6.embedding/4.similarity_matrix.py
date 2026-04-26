"""
유사도 히트맵 + 단어 유추 시각화 — 전체 쌍 유사도 행렬과 벡터 연산
- 설치: pip install sentence-transformers matplotlib seaborn numpy scikit-learn
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# 히트맵용 문장 (다양한 주제 혼합)
HEATMAP_SENTENCES = [
    "인공지능이 세상을 바꾸고 있다.",
    "딥러닝은 신경망 기반 기술이다.",
    "오늘 점심은 김치찌개를 먹었다.",
    "이탈리아 파스타가 맛있었다.",
    "축구 월드컵이 곧 시작된다.",
    "야구 경기에서 홈런이 나왔다.",
    "내일 비가 올 확률이 높다.",
    "맑은 하늘에 구름 한 점 없다.",
]

# 단어 유추용 단어 목록
ANALOGY_WORDS = {
    "왕": "왕",
    "여왕": "여왕",
    "남자": "남자",
    "여자": "여자",
    "왕자": "왕자",
    "공주": "공주",
    "아버지": "아버지",
    "어머니": "어머니",
}


def compute_similarity_matrix(embeddings):
    """코사인 유사도 행렬 계산"""
    return cosine_similarity(embeddings)


def plot_similarity_heatmap(sim_matrix, labels, filename="4.similarity_matrix.png"):
    """seaborn 히트맵으로 유사도 행렬 시각화"""
    # 라벨 줄이기
    short_labels = []
    for label in labels:
        short = label if len(label) <= 16 else label[:13] + '...'
        short_labels.append(short)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        sim_matrix,
        xticklabels=short_labels,
        yticklabels=short_labels,
        cmap="YlOrRd",
        annot=True,
        fmt=".2f",
        square=True,
        ax=ax,
        vmin=0,
        vmax=1,
        linewidths=0.5,
        linecolor='white',
    )
    ax.set_title('Sentence Similarity Matrix (Cosine Similarity)',
                 fontsize=13, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_word_analogy_2d(model, words_dict, filename="4.word_analogy.png"):
    """단어 임베딩을 2D에 투영하고 유추 관계를 화살표로 표시"""
    words = list(words_dict.keys())
    labels = list(words_dict.values())
    embeddings = model.encode(words)

    # PCA로 2D 축소
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(10, 8))

    # 단어 점 표시
    ax.scatter(coords[:, 0], coords[:, 1], s=150, c='#4C72B0',
               edgecolors='white', linewidths=1, zorder=3)

    # 라벨 표시
    for i, label in enumerate(labels):
        ax.annotate(label, (coords[i, 0], coords[i, 1]),
                    textcoords="offset points", xytext=(10, 8),
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                              edgecolor='gray', alpha=0.8))

    # 유추 화살표: 왕→여왕, 남자→여자 (성별 관계)
    arrow_pairs = [
        (words.index("왕"), words.index("여왕"), '#C44E52', 'royalty'),
        (words.index("남자"), words.index("여자"), '#55A868', 'gender'),
        (words.index("왕자"), words.index("공주"), '#DD8452', 'royalty+youth'),
        (words.index("아버지"), words.index("어머니"), '#8172B3', 'parent'),
    ]

    for src, dst, color, label in arrow_pairs:
        ax.annotate('', xy=(coords[dst, 0], coords[dst, 1]),
                    xytext=(coords[src, 0], coords[src, 1]),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2, alpha=0.7))

    # 범례
    legend_elements = [
        Line2D([0], [0], color='#C44E52', lw=2, label='royalty'),
        Line2D([0], [0], color='#55A868', lw=2, label='gender'),
        Line2D([0], [0], color='#DD8452', lw=2, label='royalty+youth'),
        Line2D([0], [0], color='#8172B3', lw=2, label='parent'),
    ]
    ax.legend(handles=legend_elements, loc='best', fontsize=10)

    # 유추 수식 표시
    analogy_text = ('"king" - "man" + "woman" ≈ "queen"\n'
                    'Vector arithmetic captures semantic relationships')
    ax.text(0.02, 0.98, analogy_text, transform=ax.transAxes,
            fontsize=10, va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    ax.set_title('Word Analogy — Vector Relationships in 2D (PCA)',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('PCA Component 1')
    ax.set_ylabel('PCA Component 2')
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def verify_analogy(model, words_dict):
    """벡터 연산으로 유추 검증: 왕 - 남자 + 여자 ≈ ?"""
    words = list(words_dict.keys())
    embeddings = model.encode(words)
    emb_dict = dict(zip(words, embeddings))

    print("\n  벡터 유추 검증:")
    # 왕 - 남자 + 여자 = ?
    result_vec = emb_dict["왕"] - emb_dict["남자"] + emb_dict["여자"]

    # 모든 단어와 유사도 계산
    sims = {}
    for word, emb in emb_dict.items():
        sim = cosine_similarity([result_vec], [emb])[0][0]
        sims[word] = sim

    print("  왕 - 남자 + 여자 = ?")
    for word, sim in sorted(sims.items(), key=lambda x: -x[1]):
        marker = " ←" if word == "여왕" else ""
        print(f"    {word}: {sim:.4f}{marker}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  유사도 히트맵 + 단어 유추 시각화")
    print("=" * 60)

    # 모델 로드
    print(f"\n  모델 로드: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # ── 1. 유사도 히트맵 ──
    print("\n[ 1. 유사도 히트맵 ]")
    print("-" * 40)

    embeddings = model.encode(HEATMAP_SENTENCES)
    sim_matrix = compute_similarity_matrix(embeddings)
    print(f"  {len(HEATMAP_SENTENCES)}개 문장 × {len(HEATMAP_SENTENCES)}개 유사도 행렬")

    # 가장 유사한 쌍 찾기 (대각선 제외)
    np.fill_diagonal(sim_matrix, 0)
    max_idx = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
    print(f"  가장 유사한 쌍: [{max_idx[0]}] vs [{max_idx[1]}] = {sim_matrix[max_idx]:.4f}")
    print(f"    → {HEATMAP_SENTENCES[max_idx[0]]}")
    print(f"    → {HEATMAP_SENTENCES[max_idx[1]]}")

    # 히트맵 원본 복원 (대각선 1.0)
    np.fill_diagonal(sim_matrix, 1.0)
    plot_similarity_heatmap(sim_matrix, HEATMAP_SENTENCES, "results/4.similarity_matrix.png")

    # ── 2. 단어 유추 ──
    print("\n[ 2. 단어 유추 (Word Analogy) ]")
    print("-" * 40)
    verify_analogy(model, ANALOGY_WORDS)
    plot_word_analogy_2d(model, ANALOGY_WORDS, "results/4.word_analogy.png")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 유사도 히트맵:
   - 같은 주제 문장끼리 높은 유사도 (대각선 블록 패턴)
   - AI↔AI, 음식↔음식, 스포츠↔스포츠 등 클러스터 확인
   - 이 행렬이 검색 엔진의 랭킹 기반

2. 단어 유추 (Word Analogy):
   - "왕 - 남자 + 여자 ≈ 여왕" — 벡터 산술로 의미 관계 포착
   - 성별, 지위 등의 의미적 축이 벡터 공간에 인코딩
   - Word2Vec에서 처음 발견, 현대 모델에서도 유지

3. 한계점:
   - 문장 임베딩 모델은 단어 유추가 완벽하지 않을 수 있음
   - 단어 유추는 Word2Vec/FastText에서 더 뚜렷
   - 문장 레벨 모델은 문맥 전체를 고려하므로 단어 단위 연산이 약할 수 있음

4. 실용적 활용:
   - 유사도 행렬 → 추천 시스템, 중복 문서 탐지
   - 벡터 연산 → 데이터 증강, 의미 검색 개선
""")


if __name__ == "__main__":
    main()
