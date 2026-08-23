"""
포지셔널 인코딩(Positional Encoding) — Transformer는 왜 순서 정보를 따로 넣어줘야 하는가
- 설치: pip install torch matplotlib numpy

7.attention 에서 본 self-attention 계산(QK^T → softmax → ×V)을 잘 보면, 그 어디에도
"몇 번째 토큰인지"는 등장하지 않는다 — 순서를 뒤섞어도 attention 계산 자체는 똑같이 된다
(집합 연산이라 순서에 무관하다, "permutation invariant"). 그래서 Transformer는 입력 임베딩에
'위치 정보'를 명시적으로 더해준다 — 그게 포지셔널 인코딩이다.
"""
import os
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
# Windows는 'Malgun Gothic', macOS/Linux는 'NanumGothic'이 흔히 설치돼 있다.
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def sinusoidal_positional_encoding(seq_len: int, d_model: int) -> np.ndarray:
    """원 논문(Attention Is All You Need) 공식의 sin/cos 포지셔널 인코딩.

    짝수 차원엔 sin, 홀수 차원엔 cos을 쓰고, 차원마다 주파수(파장)를 다르게 준다 —
    낮은 차원은 빠르게 진동(위치 변화에 민감), 높은 차원은 느리게 진동(넓은 범위를 구분).
    """
    position = np.arange(seq_len)[:, np.newaxis]          # (seq_len, 1)
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))  # (d_model/2,)

    pe = np.zeros((seq_len, d_model))
    pe[:, 0::2] = np.sin(position * div_term)  # 짝수 인덱스
    pe[:, 1::2] = np.cos(position * div_term)  # 홀수 인덱스
    return pe


def plot_pe_heatmap(pe: np.ndarray, filename: str):
    """포지셔널 인코딩 전체를 히트맵으로 — 낮은 차원일수록 줄무늬가 촘촘하다(고주파)."""
    plt.figure(figsize=(12, 6))
    plt.imshow(pe.T, cmap="RdBu_r", aspect="auto")
    plt.colorbar(label="값")
    plt.xlabel("위치(Position)")
    plt.ylabel("차원(Dimension)")
    plt.title("포지셔널 인코딩 — 위치 x 차원\n"
               "차원마다 다른 주파수의 sin/cos 파동 (낮은 차원=빠른 진동, 높은 차원=느린 진동)")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def plot_pe_waves(pe: np.ndarray, filename: str):
    """특정 차원 몇 개를 파형(sin 곡선)으로 — 왜 '파동'이라 부르는지 직관적으로 보여준다."""
    dims_to_show = [0, 1, 4, 5, 20, 21]
    plt.figure(figsize=(12, 6))
    for d in dims_to_show:
        kind = "sin" if d % 2 == 0 else "cos"
        plt.plot(pe[:, d], label=f"dim {d} ({kind})", marker="o", markersize=3)
    plt.xlabel("위치(Position)")
    plt.ylabel("값")
    plt.title("일부 차원의 포지셔널 인코딩 파형 — 차원마다 주파수가 다르다")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def plot_position_similarity(pe: np.ndarray, filename: str):
    """위치 벡터끼리의 코사인 유사도 — 가까운 위치일수록 유사도가 높다(상대적 거리 정보 보존)."""
    norm = pe / np.linalg.norm(pe, axis=1, keepdims=True)
    sim = norm @ norm.T

    plt.figure(figsize=(7, 6))
    plt.imshow(sim, cmap="viridis")
    plt.colorbar(label="코사인 유사도")
    plt.xlabel("위치")
    plt.ylabel("위치")
    plt.title("위치 벡터 간 코사인 유사도\n"
               "대각선(같은 위치)이 가장 밝고, 멀어질수록 어두워진다 — '거리' 정보가 담겨있다")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def demonstrate_permutation_invariance():
    """attention이 순서에 무관하다는 걸 숫자로 직접 확인 — PE 없이 QK^T만 계산."""
    np.random.seed(0)
    d_model = 8
    # "cat", "sat", "mat" 세 단어의 가짜 임베딩 (실제 값은 중요치 않다, 순서 실험이 목적)
    emb = {"cat": np.random.randn(d_model), "sat": np.random.randn(d_model),
           "mat": np.random.randn(d_model)}

    def attention_output(order):
        X = np.stack([emb[w] for w in order])       # (3, d_model)
        scores = X @ X.T / np.sqrt(d_model)          # QK^T (Q=K=X로 단순화)
        weights = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)  # softmax
        return weights @ X                            # ×V (V=X로 단순화)

    out_forward = attention_output(["cat", "sat", "mat"])
    out_shuffled = attention_output(["mat", "sat", "cat"])

    # "cat" 토큰이 만들어내는 출력만 비교 — 순서가 바뀌어도 같은 단어의 attention 출력이 같은지
    cat_idx_forward = 0    # forward: cat이 0번째
    cat_idx_shuffled = 2   # shuffled: cat이 2번째
    same = np.allclose(out_forward[cat_idx_forward], out_shuffled[cat_idx_shuffled])

    print(f"  'cat sat mat' 순서에서 'cat'의 attention 출력: {out_forward[cat_idx_forward][:3].round(3)} ...")
    print(f"  'mat sat cat' 순서에서 'cat'의 attention 출력: {out_shuffled[cat_idx_shuffled][:3].round(3)} ...")
    print(f"  → 완전히 같은가? {same}  (PE 없이는 문장 안에서의 위치가 바뀌어도 출력이 똑같다!)")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  포지셔널 인코딩(Positional Encoding)")
    print("=" * 60)

    print("\n[ 1. Attention은 순서를 모른다 — 직접 확인 ]")
    print("-" * 40)
    demonstrate_permutation_invariance()

    print("\n[ 2. sin/cos 포지셔널 인코딩 계산 ]")
    print("-" * 40)
    seq_len, d_model = 50, 64
    pe = sinusoidal_positional_encoding(seq_len, d_model)
    print(f"  seq_len={seq_len}, d_model={d_model} → PE shape: {pe.shape}")

    print("\n[ 3. 시각화 ]")
    print("-" * 40)
    plot_pe_heatmap(pe, "results/1.pe_heatmap.png")
    plot_pe_waves(pe, "results/1.pe_waves.png")
    plot_position_similarity(pe, "results/1.pe_similarity.png")

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. Attention은 그 자체로 "순서를 모른다":
   - QK^T → softmax → ×V 계산 어디에도 "몇 번째 토큰인지"가 없다
   - 토큰 순서를 섞어도 각 토큰의 attention 출력(자기 자신 기준 상대적 결과)은 동일하다
   - RNN은 한 스텝씩 순서대로 처리해서 순서가 구조에 내장되지만, attention은 그렇지 않다

2. 그래서 포지셔널 인코딩을 "더한다":
   - 최종 입력 = 토큰 임베딩 + 위치 임베딩(같은 차원이라 그냥 더할 수 있다)
   - sin/cos을 쓰는 이유: 학습 안 해도 미리 계산 가능하고, 훈련 때 못 본 긴 문장에도 확장 가능

3. 왜 하필 sin/cos 파동인가:
   - 차원마다 다른 주파수를 쓰면, 위치 조합마다 고유한 패턴이 만들어진다(이진수 자리수와 비슷한 원리)
   - 위치 p와 p+k 사이의 관계가 선형 변환으로 표현 가능해서, 모델이 "상대적 거리"를 학습하기 쉽다
   - 위 유사도 그림에서 가까운 위치일수록 밝은 것도 이 성질 때문이다

4. 현대 모델은 조금씩 다른 방식도 쓴다(참고만):
   - RoPE(Rotary Position Embedding): Llama/Qwen 등 최신 모델 다수가 사용, 회전 변환으로 상대
     위치를 인코딩. 여기서 쓴 sin/cos '절대 위치' 방식과 목적은 같지만 구현이 다르다.
   - 학습 가능한 위치 임베딩(BERT 등): sin/cos 공식 대신 위치별 벡터 자체를 학습 파라미터로 둔다.
""")


if __name__ == "__main__":
    main()
