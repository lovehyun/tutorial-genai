"""
2D 벡터 공간 시각화 — PCA/t-SNE로 문장 임베딩을 2D에 투영, 카테고리별 클러스터 확인
- 설치: pip install sentence-transformers matplotlib numpy scikit-learn
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

CATEGORIZED_SENTENCES = {
    "Tech/AI": [
        "인공지능이 의료 분야를 혁신하고 있다.",
        "딥러닝은 이미지 인식에 뛰어난 성능을 보인다.",
        "자연어 처리 기술이 빠르게 발전하고 있다.",
        "GPT 모델은 텍스트 생성에 사용된다.",
    ],
    "Food": [
        "김치찌개는 한국의 대표적인 음식이다.",
        "이탈리아 파스타는 다양한 소스와 잘 어울린다.",
        "신선한 초밥은 일본 요리의 정수다.",
        "프랑스 빵은 바삭한 겉과 부드러운 속이 특징이다.",
    ],
    "Sports": [
        "축구는 전 세계에서 가장 인기 있는 스포츠다.",
        "야구 시즌이 시작되면 경기장이 관중으로 가득 찬다.",
        "수영은 전신 운동으로 건강에 매우 좋다.",
        "농구는 빠른 속도와 화려한 기술이 매력이다.",
    ],
    "Weather": [
        "오늘 서울의 기온은 영하 5도로 매우 춥다.",
        "장마철에는 습도가 높아 불쾌지수가 올라간다.",
        "가을 하늘은 맑고 높아서 산책하기 좋다.",
        "태풍이 접근하면서 강풍과 폭우가 예상된다.",
    ],
}

# 카테고리별 색상과 마커
CATEGORY_STYLES = {
    "Tech/AI": {"color": "#4C72B0", "marker": "o"},
    "Food":    {"color": "#DD8452", "marker": "s"},
    "Sports":  {"color": "#55A868", "marker": "^"},
    "Weather": {"color": "#C44E52", "marker": "D"},
}


def embed_sentences(model, categorized):
    """카테고리별 문장을 임베딩하고 (embeddings, labels, categories) 반환"""
    all_sentences = []
    all_labels = []
    all_categories = []

    for category, sentences in categorized.items():
        for sent in sentences:
            all_sentences.append(sent)
            short = sent if len(sent) <= 18 else sent[:15] + '...'
            all_labels.append(short)
            all_categories.append(category)

    embeddings = model.encode(all_sentences)
    return embeddings, all_labels, all_categories


def reduce_to_2d(embeddings, method="pca"):
    """PCA 또는 t-SNE로 차원 축소"""
    if method == "pca":
        reducer = PCA(n_components=2, random_state=42)
    elif method == "tsne":
        reducer = TSNE(n_components=2, random_state=42, perplexity=5, max_iter=1000)
    else:
        raise ValueError(f"Unknown method: {method}")
    return reducer.fit_transform(embeddings)


def plot_vector_space_2d(coords, labels, categories, method_name, filename):
    """카테고리별 색상+마커 산점도 + 클러스터 영역"""
    fig, ax = plt.subplots(figsize=(12, 9))

    # 카테고리별로 플롯
    unique_cats = list(dict.fromkeys(categories))  # 순서 유지
    for cat in unique_cats:
        style = CATEGORY_STYLES[cat]
        indices = [i for i, c in enumerate(categories) if c == cat]
        cat_coords = coords[indices]

        ax.scatter(cat_coords[:, 0], cat_coords[:, 1],
                   c=style["color"], marker=style["marker"],
                   s=120, label=cat, edgecolors='white', linewidths=0.5, zorder=3)

        # 클러스터 영역 (convex hull 느낌으로 원 표시)
        cx, cy = cat_coords[:, 0].mean(), cat_coords[:, 1].mean()
        radius = np.max(np.sqrt(np.sum((cat_coords - [cx, cy]) ** 2, axis=1))) * 1.2
        circle = plt.Circle((cx, cy), radius, color=style["color"],
                             alpha=0.08, zorder=1)
        ax.add_patch(circle)

    # 라벨 표시
    for i, label in enumerate(labels):
        ax.annotate(label, (coords[i, 0], coords[i, 1]),
                    textcoords="offset points", xytext=(8, 5),
                    fontsize=7, alpha=0.8)

    ax.set_xlabel(f'{method_name} Component 1')
    ax.set_ylabel(f'{method_name} Component 2')
    ax.set_title(f'Sentence Embeddings in 2D ({method_name})\n'
                 f'Similar sentences cluster together',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_pca_vs_tsne(embeddings, labels, categories, filename="3.pca_vs_tsne.png"):
    """PCA와 t-SNE 결과를 나란히 비교"""
    coords_pca = reduce_to_2d(embeddings, "pca")
    coords_tsne = reduce_to_2d(embeddings, "tsne")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    unique_cats = list(dict.fromkeys(categories))

    for ax, coords, title in [(ax1, coords_pca, "PCA"), (ax2, coords_tsne, "t-SNE")]:
        for cat in unique_cats:
            style = CATEGORY_STYLES[cat]
            indices = [i for i, c in enumerate(categories) if c == cat]
            cat_coords = coords[indices]
            ax.scatter(cat_coords[:, 0], cat_coords[:, 1],
                       c=style["color"], marker=style["marker"],
                       s=120, label=cat, edgecolors='white', linewidths=0.5)

        for i, label in enumerate(labels):
            ax.annotate(label, (coords[i, 0], coords[i, 1]),
                        textcoords="offset points", xytext=(8, 5),
                        fontsize=7, alpha=0.8)

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(f'{title} Component 1')
        ax.set_ylabel(f'{title} Component 2')
        ax.legend(loc='best', fontsize=9)
        ax.grid(alpha=0.2)

    plt.suptitle('PCA vs t-SNE — Dimensionality Reduction Comparison',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  2D 벡터 공간 시각화")
    print("=" * 60)

    # 모델 로드
    print(f"\n  모델 로드: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # 임베딩 생성
    print("\n[ 1. 문장 임베딩 생성 ]")
    print("-" * 40)
    embeddings, labels, categories = embed_sentences(model, CATEGORIZED_SENTENCES)
    print(f"  총 {len(labels)}개 문장, {len(set(categories))}개 카테고리")
    print(f"  임베딩 shape: {embeddings.shape}")

    # ── PCA 시각화 ──
    print("\n[ 2. PCA 2D 시각화 ]")
    print("-" * 40)
    coords_pca = reduce_to_2d(embeddings, "pca")
    plot_vector_space_2d(coords_pca, labels, categories, "PCA", "results/3.vector_space_2d.png")

    # ── PCA vs t-SNE 비교 ──
    print("\n[ 3. PCA vs t-SNE 비교 ]")
    print("-" * 40)
    plot_pca_vs_tsne(embeddings, labels, categories, "results/3.pca_vs_tsne.png")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 벡터 공간의 의미:
   - 비슷한 의미의 문장은 벡터 공간에서 가까이 위치
   - 다른 주제의 문장은 멀리 위치 → 클러스터 형성
   - 이것이 시맨틱 검색, 추천 시스템의 핵심 원리

2. 차원 축소 기법:
   - PCA: 분산을 최대로 보존하는 선형 투영 (빠르고 결정적)
   - t-SNE: 이웃 관계를 보존하는 비선형 투영 (클러스터 분리가 뚜렷)
   - 384차원 → 2차원으로 줄이면 정보 손실 불가피

3. 실용적 활용:
   - RAG: 질문과 가장 가까운 문서 벡터를 검색
   - 분류: 벡터 공간에서 카테고리 경계를 학습
   - 클러스터링: 비슷한 문장을 자동으로 그룹화

4. 모델 선택:
   - paraphrase-multilingual-MiniLM: 경량(384차원), 50+언어
   - 더 정확한 결과가 필요하면 더 큰 모델 사용
""")


if __name__ == "__main__":
    main()
