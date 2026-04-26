# 임베딩 시각화 (Embedding Visualization)

텍스트 → 토큰 → 벡터 → 벡터 공간의 전체 파이프라인을 시각적으로 이해하는 예제입니다.

## 파이프라인

```
문장 입력 → 토큰화(서브워드 분할) → 임베딩(벡터 변환) → 벡터 공간(유사도 비교)
```

## 파일 구조

| 파일 | 설명 | 출력 |
|------|------|------|
| `1.tokenize_visualize.py` | 토큰화 과정 시각화 (3개 토크나이저 비교) | `tokenize_comparison.png`, `tokenize_counts.png` |
| `2.embedding_visualize.py` | 임베딩 벡터 구조 + 유사/비유사 문장 비교 | `embedding_vector.png`, `embedding_compare_*.png`, `similarity_bars.png` |
| `3.vector_space_2d.py` | 16문장을 2D에 투영, 카테고리별 클러스터 확인 | `vector_space_2d.png`, `pca_vs_tsne.png` |
| `4.similarity_matrix.py` | 유사도 히트맵 + 단어 유추(왕-남자+여자≈여왕) | `similarity_matrix.png`, `word_analogy.png` |
| `5.vector_space_3d.py` | 3D 벡터 공간 산점도 + 클러스터 간 거리 | `vector_space_3d.png`, `vector_space_3d_distances.png` |

모든 결과 이미지는 `results/` 폴더에 저장됩니다.

## 설치

```bash
pip install transformers sentencepiece sentence-transformers matplotlib seaborn numpy scikit-learn
```

## 사용 모델

- **토크나이저**: BERT WordPiece, GPT-2 BPE, T5 SentencePiece
- **임베딩**: `paraphrase-multilingual-MiniLM-L12-v2` (384차원, 50+언어 지원)

## 학습 순서

각 파일은 순서대로 학습하면 자연스럽게 연결됩니다.

### 1단계: 토큰화 (`1.tokenize_visualize.py`)

문장이 모델에 들어가기 전 **서브워드(subword)** 단위로 쪼개지는 과정입니다.

- 같은 문장이라도 토크나이저에 따라 분할 방식이 다름
- **WordPiece** (BERT): `인공지능이` → `인`, `##공`, `##지`, `##능`, `##이` (12토큰)
- **BPE** (GPT-2): 한국어를 바이트 단위로 쪼개 36토큰 — 비효율적
- **SentencePiece** (T5): 한국어 어절 단위로 분할해 9토큰 — 효율적
- 핵심: **토큰 수 = API 비용**, 한국어 특화 토크나이저의 중요성

### 2단계: 임베딩 벡터 (`2.embedding_visualize.py`)

토큰화된 문장이 **고정 길이 숫자 배열(384차원 벡터)** 로 변환되는 과정입니다.

- 각 차원은 의미적 특성을 인코딩 (양수/음수 혼재)
- "인공지능이 세상을 바꾸고 있다" ≈ "AI가 세계를 변화시키고 있다" → 유사한 벡터
- "날씨가 좋다" vs "피자를 먹고 싶다" → 매우 다른 벡터
- **코사인 유사도**: 두 벡터의 방향이 얼마나 같은지 (0~1)

### 3단계: 2D 벡터 공간 (`3.vector_space_2d.py`)

384차원 벡터를 **PCA/t-SNE로 2D에 투영**해서 클러스터를 눈으로 확인합니다.

- 같은 카테고리(AI, 음식, 스포츠, 날씨) 문장끼리 가까이 모임
- PCA: 분산을 최대 보존하는 선형 투영 (빠르고 결정적)
- t-SNE: 이웃 관계를 보존하는 비선형 투영 (클러스터가 뚜렷)
- 이것이 **시맨틱 검색, RAG, 추천 시스템**의 핵심 원리

### 4단계: 유사도 + 단어 유추 (`4.similarity_matrix.py`)

전체 문장 쌍의 유사도 히트맵과 벡터 산술(word analogy)입니다.

- 히트맵에서 같은 주제끼리 높은 유사도 블록 패턴 관찰
- **벡터 연산**: `왕 - 남자 + 여자 ≈ 여왕` — 의미 관계가 벡터에 인코딩됨
- 이 행렬이 검색 엔진의 랭킹, 중복 문서 탐지의 기반

### 5단계: 3D 벡터 공간 (`5.vector_space_3d.py`)

2D보다 **더 많은 정보를 보존**하는 3D 입체 시각화입니다.

- 두 시점에서 촬영하여 깊이감 제공
- 클러스터 간 코사인 유사도를 점선으로 표시
- 2D에서 겹쳐 보이던 점들이 3D에서 분리되는 것을 확인
- PCA 설명 분산: 2D ~30% vs 3D ~41% (정보 보존량 향상)
