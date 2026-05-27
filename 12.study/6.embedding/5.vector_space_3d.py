"""
3D 벡터 공간 시각화 — PCA로 문장 임베딩을 3D에 투영, 회전 가능한 입체 산점도
- 설치: pip install sentence-transformers matplotlib numpy scikit-learn
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

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

CATEGORY_STYLES = {
    "Tech/AI": {"color": "#4C72B0", "marker": "o"},
    "Food":    {"color": "#DD8452", "marker": "s"},
    "Sports":  {"color": "#55A868", "marker": "^"},
    "Weather": {"color": "#C44E52", "marker": "D"},
}


def embed_sentences(model, categorized):
    """카테고리별 문장을 임베딩하고 (embeddings, sentences, labels, categories) 반환"""
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
    return embeddings, all_sentences, all_labels, all_categories


def plot_vector_space_3d(coords, labels, categories, filename="5.vector_space_3d.png"):
    """3D 산점도 — 카테고리별 색상+마커, 두 시점에서 촬영"""
    fig = plt.figure(figsize=(20, 9))

    # 두 시점에서 보기
    views = [(25, 45), (25, 135)]
    view_titles = ["View 1 (front)", "View 2 (side)"]

    unique_cats = list(dict.fromkeys(categories))

    for v_idx, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, 2, v_idx + 1, projection='3d')

        for cat in unique_cats:
            style = CATEGORY_STYLES[cat]
            indices = [i for i, c in enumerate(categories) if c == cat]
            cat_coords = coords[indices]

            ax.scatter(cat_coords[:, 0], cat_coords[:, 1], cat_coords[:, 2],
                       c=style["color"], marker=style["marker"],
                       s=100, label=cat, edgecolors='white', linewidths=0.5,
                       depthshade=True, alpha=0.9)

        # 라벨 표시
        for i, label in enumerate(labels):
            ax.text(coords[i, 0], coords[i, 1], coords[i, 2], f' {label}',
                    fontsize=6, alpha=0.7)

        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_zlabel('PC3')
        ax.set_title(view_titles[v_idx], fontsize=12)
        ax.view_init(elev=elev, azim=azim)
        ax.legend(loc='upper left', fontsize=8)

    plt.suptitle('Sentence Embeddings in 3D Vector Space (PCA)\n'
                 'Similar sentences cluster together in 3D',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def plot_3d_with_distances(coords, labels, categories, embeddings, filename="5.vector_space_3d_distances.png"):
    """3D 산점도 + 카테고리 간 거리를 점선으로 표시"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    unique_cats = list(dict.fromkeys(categories))

    # 카테고리별 중심점 계산
    centroids = {}
    for cat in unique_cats:
        style = CATEGORY_STYLES[cat]
        indices = [i for i, c in enumerate(categories) if c == cat]
        cat_coords = coords[indices]

        ax.scatter(cat_coords[:, 0], cat_coords[:, 1], cat_coords[:, 2],
                   c=style["color"], marker=style["marker"],
                   s=100, label=cat, edgecolors='white', linewidths=0.5,
                   depthshade=True, alpha=0.9)

        centroids[cat] = cat_coords.mean(axis=0)

    # 카테고리 중심 간 거리선 (코사인 유사도 표시)
    cat_list = list(centroids.keys())
    for i in range(len(cat_list)):
        for j in range(i + 1, len(cat_list)):
            c1, c2 = centroids[cat_list[i]], centroids[cat_list[j]]
            # 원본 임베딩으로 코사인 유사도 계산
            idx_i = [k for k, c in enumerate(categories) if c == cat_list[i]]
            idx_j = [k for k, c in enumerate(categories) if c == cat_list[j]]
            sim = cosine_similarity(
                embeddings[idx_i].mean(axis=0, keepdims=True),
                embeddings[idx_j].mean(axis=0, keepdims=True)
            )[0][0]

            ax.plot([c1[0], c2[0]], [c1[1], c2[1]], [c1[2], c2[2]],
                    'k--', alpha=0.3, linewidth=1)
            mid = (c1 + c2) / 2
            ax.text(mid[0], mid[1], mid[2], f'{sim:.2f}',
                    fontsize=8, ha='center', color='gray',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

    # 라벨
    for i, label in enumerate(labels):
        ax.text(coords[i, 0], coords[i, 1], coords[i, 2], f' {label}',
                fontsize=6, alpha=0.7)

    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_zlabel('PC3')
    ax.set_title('3D Vector Space with Inter-Cluster Similarity',
                 fontsize=13, fontweight='bold')
    ax.view_init(elev=20, azim=60)
    ax.legend(loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  저장: {filename}")


def print_distance_matrix(embeddings, categories):
    """카테고리 간 평균 코사인 유사도 출력"""
    unique_cats = list(dict.fromkeys(categories))
    cat_embeddings = {}
    for cat in unique_cats:
        indices = [i for i, c in enumerate(categories) if c == cat]
        cat_embeddings[cat] = embeddings[indices].mean(axis=0, keepdims=True)

    print(f"\n  {'':>12}", end='')
    for cat in unique_cats:
        print(f"  {cat:>10}", end='')
    print()
    print("  " + "-" * (12 + 12 * len(unique_cats)))

    for cat_i in unique_cats:
        print(f"  {cat_i:>12}", end='')
        for cat_j in unique_cats:
            sim = cosine_similarity(cat_embeddings[cat_i], cat_embeddings[cat_j])[0][0]
            print(f"  {sim:>10.3f}", end='')
        print()


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  3D 벡터 공간 시각화")
    print("=" * 60)

    # 모델 로드
    print(f"\n  모델 로드: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # 임베딩 생성
    print("\n[ 1. 문장 임베딩 생성 ]")
    print("-" * 40)
    embeddings, sentences, labels, categories = embed_sentences(model, CATEGORIZED_SENTENCES)
    print(f"  총 {len(labels)}개 문장, {len(set(categories))}개 카테고리")
    print(f"  임베딩 shape: {embeddings.shape}")

    # PCA 3D 축소
    print("\n[ 2. PCA 3D 시각화 ]")
    print("-" * 40)
    pca = PCA(n_components=3, random_state=42)
    coords = pca.fit_transform(embeddings)
    explained = pca.explained_variance_ratio_
    print(f"  PCA 설명 분산: PC1={explained[0]:.1%}, PC2={explained[1]:.1%}, PC3={explained[2]:.1%}")
    print(f"  총 설명 분산: {sum(explained):.1%} (2D: {sum(explained[:2]):.1%})")

    plot_vector_space_3d(coords, labels, categories, "results/5.vector_space_3d.png")

    # 거리 포함 3D
    print("\n[ 3. 클러스터 간 거리 시각화 ]")
    print("-" * 40)
    plot_3d_with_distances(coords, labels, categories, embeddings, "results/5.vector_space_3d_distances.png")

    # 카테고리 간 유사도 행렬
    print("\n[ 4. 카테고리 간 평균 유사도 ]")
    print("-" * 40)
    print_distance_matrix(embeddings, categories)

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 3D vs 2D:
   - 3D는 2D보다 더 많은 분산을 보존 (정보 손실 감소)
   - 2D: PC1+PC2만 사용 → 3D: PC3까지 추가로 거리 표현
   - 2D에서 겹쳐 보이던 점들이 3D에서 분리될 수 있음

2. PCA 설명 분산:
   - 각 축이 원본 데이터의 몇 %를 설명하는지 표시
   - PC1 > PC2 > PC3 순으로 중요도 감소
   - 384차원 → 3차원이므로 여전히 정보 손실 존재

3. 클러스터 간 거리:
   - 같은 카테고리 내: 높은 유사도 (점들이 가까이 모임)
   - 다른 카테고리 간: 낮은 유사도 (클러스터가 멀리 분리)
   - 이 거리가 RAG 검색, 분류의 정확도를 결정

4. 실용적 인사이트:
   - 벡터 DB(FAISS, ChromaDB)는 이 공간에서 최근접 이웃 검색
   - 차원 축소 없이 384차원 그대로 검색 → 정보 손실 없음
   - 시각화는 이해용, 실제 검색은 원본 차원에서 수행
""")


if __name__ == "__main__":
    main()
