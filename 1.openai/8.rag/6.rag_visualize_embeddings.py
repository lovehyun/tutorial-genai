# RAG with FAISS - 6단계: 임베딩·거리 계산 디버깅 시각화
# pip install faiss-cpu numpy matplotlib scikit-learn sentence-transformers
#
# 1~5단계까지는 검색 결과를 '숫자'(거리·유사도 점수)로만 확인했다.
# 6단계는 그 숫자가 나온 벡터 공간을 '눈으로' 본다:
#   ① 문서 벡터들이 공간의 어디에 있는지
#   ② 질문 벡터는 그중 어디에 있는지
#   ③ FAISS가 실제로 측정한 거리가 그림 위에서 어떻게 보이는지
#
# 로컬 임베딩 모델을 쓰므로 API 키가 필요 없다 — 그림이 마음에 안 들면 문서/질문을
# 바꿔가며 몇 번이고 무료로 다시 돌려볼 수 있다 (3단계와 같은 이유).
#
# 주의: 사람 눈에 보이는 건 384차원을 2차원으로 억지로 눌러 담은(PCA) '근사 지도'다.
#       그림 속 점 사이 거리와, 선 위에 적힌 실제 거리 숫자가 다를 수 있다 —
#       숫자는 원본 384차원에서 FAISS가 직접 측정한 '진짜' 값이다.

import os
import warnings
import numpy as np
import faiss
import matplotlib
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
# Windows는 'Malgun Gothic', macOS/Linux는 'NanumGothic'이 흔히 설치돼 있다.
# 셋 다 없으면 한글이 네모 박스(□)로 깨져 나온다 — 그럴 땐 나눔고딕 등을 설치할 것.
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 1.rag_basic.py와 같은 문서/질문 — 지금까지 배운 단계와 바로 비교할 수 있도록.
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]
query = "Python은 어떤 언어인가요?"


def build_index(docs):
    """문서를 임베딩하고 FAISS(IndexFlatL2) 인덱스에 저장한다."""
    doc_embeddings = np.array(embedding_model.encode(docs), dtype=np.float32)
    index = faiss.IndexFlatL2(doc_embeddings.shape[1])
    index.add(doc_embeddings)
    return index, doc_embeddings


def search(index, doc_embeddings, query_text, docs):
    """질문을 임베딩하고, FAISS로 '진짜'(원본 차원) 거리를 측정한다."""
    query_embedding = np.array([embedding_model.encode(query_text)], dtype=np.float32)

    # [관전 포인트 1] k=len(docs) — 순위를 매기기 위해 문서 전부와의 거리를 구한다
    #   (실전 RAG처럼 top-1만 보는 게 아니라, 디버깅이 목적이라 전체를 다 본다)
    distances, indices = index.search(query_embedding, k=len(docs))

    # FAISS가 반환하는 순서(가까운 순)를 다시 원래 문서 순서로 정렬 — 그래프에서 헷갈리지 않게
    order = np.argsort(indices[0])
    real_distances = np.sqrt(distances[0][order])  # IndexFlatL2는 '거리의 제곱'을 반환
    return query_embedding, real_distances


def plot_debug_view(doc_embeddings, query_embedding, real_distances, docs, query_text, filename):
    """왼쪽: 2D로 눌러본 벡터 공간(문서+질문+거리선). 오른쪽: 실제 거리 막대그래프."""
    # [관전 포인트 2] PCA — 384차원 벡터를 사람이 볼 수 있는 2차원으로 투영
    #   문서 3개 + 질문 1개, 총 4개 점을 '같은 좌표계'로 함께 투영해야 위치 비교가 의미 있다.
    all_vectors = np.vstack([doc_embeddings, query_embedding])
    coords_2d = PCA(n_components=2, random_state=42).fit_transform(all_vectors)
    doc_coords, query_coord = coords_2d[:-1], coords_2d[-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # --- 왼쪽: 벡터 공간 산점도 ---
    labels = [d if len(d) <= 20 else d[:17] + '...' for d in docs]
    ax1.scatter(doc_coords[:, 0], doc_coords[:, 1], c='#4C72B0', marker='o',
                s=180, label='문서(document)', edgecolors='white', linewidths=1, zorder=3)
    ax1.scatter(*query_coord, c='#C44E52', marker='*',
                s=400, label='질문(query)', edgecolors='white', linewidths=1, zorder=4)

    for i, label in enumerate(labels):
        ax1.annotate(label, doc_coords[i], textcoords="offset points",
                     xytext=(10, 6), fontsize=9)
    ax1.annotate('질문', query_coord, textcoords="offset points",
                 xytext=(10, -14), fontsize=9, fontweight='bold', color='#C44E52')

    # [관전 포인트 3] 질문→문서 거리선 — 선 위의 숫자는 그림(2D)이 아니라 원본(384D) 거리
    for i in range(len(docs)):
        ax1.plot([query_coord[0], doc_coords[i, 0]], [query_coord[1], doc_coords[i, 1]],
                  '--', color='gray', alpha=0.5, zorder=1)
        mid = (query_coord + doc_coords[i]) / 2
        ax1.annotate(f'{real_distances[i]:.3f}', mid, fontsize=9, color='dimgray',
                     ha='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.8))

    ax1.set_title('벡터 공간 (PCA로 2D 투영)\n선 위 숫자 = FAISS가 측정한 실제 L2 거리(384D)', fontsize=11)
    ax1.set_xlabel('PCA Component 1')
    ax1.set_ylabel('PCA Component 2')
    ax1.legend(loc='best')
    ax1.grid(alpha=0.2)

    # --- 오른쪽: 실제 거리 막대그래프 (가까운 순 정렬) ---
    rank_order = np.argsort(real_distances)
    ranked_labels = [labels[i] for i in rank_order]
    ranked_distances = [real_distances[i] for i in rank_order]
    colors = ['#55A868' if i == 0 else '#4C72B0' for i in range(len(ranked_labels))]

    bars = ax2.barh(range(len(ranked_labels)), ranked_distances, color=colors)
    ax2.set_yticks(range(len(ranked_labels)))
    ax2.set_yticklabels(ranked_labels)
    ax2.invert_yaxis()  # 가장 가까운(=값이 작은) 문서를 맨 위로
    ax2.set_xlabel('L2 거리 (작을수록 유사)')
    ax2.set_title(f'질문 "{query_text}"과(와)의 거리\n(초록 = 가장 가까운 문서)', fontsize=11)
    for bar, dist in zip(bars, ranked_distances):
        ax2.annotate(f'{dist:.3f}', (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                     xytext=(6, 0), textcoords='offset points', va='center', fontsize=9)
    ax2.grid(alpha=0.2, axis='x')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)

    print(f"질문: {query}\n")
    index, doc_embeddings = build_index(documents)
    query_embedding, real_distances = search(index, doc_embeddings, query, documents)

    # [디버깅용 콘솔 출력] 그림을 보기 전에 숫자로 먼저 확인
    print(f"임베딩 차원: {doc_embeddings.shape[1]}")
    for doc, dist in sorted(zip(documents, real_distances), key=lambda x: x[1]):
        print(f"  거리 {dist:.4f}  ←  {doc}")

    plot_debug_view(doc_embeddings, query_embedding, real_distances, documents, query,
                     "results/6.rag_visualize_embeddings.png")


if __name__ == "__main__":
    main()
