"""
RNN → Transformer 전환 배경 — 기울기 소실과 병렬화
- 설치: pip install torch matplotlib numpy

Transformer(2017) 이전엔 RNN/LSTM이 시퀀스 처리의 표준이었다. Transformer가 그 자리를 대체한
이유는 크게 두 가지다: ① RNN은 먼 과거의 정보가 학습 신호(gradient)로 잘 안 돌아온다(기울기
소실), ② RNN은 한 스텝씩 순서대로만 계산할 수 있어 병렬화가 안 된다. 이 두 가지를 직접 측정해서
확인한다 — `7.attention`에서 이미 attention이 "모든 위치를 한 번에" 계산하는 걸 봤는데, 그게
왜 중요한지의 답이 여기 있다.
"""
import os
import time
import logging
import warnings
import torch
import torch.nn as nn
import matplotlib
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
# 로그 스케일 축의 지수 표기(예: 10⁻¹⁴)에 쓰이는 유니코드 마이너스 글꼴이 폴백 폰트에 없어서
# 나는 콘솔 경고 — matplotlib이 warnings가 아니라 logging으로 찍기 때문에 로거로 꺼야 한다.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
logging.getLogger("matplotlib.mathtext").setLevel(logging.ERROR)
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

torch.manual_seed(0)


def vanishing_gradient_experiment(seq_len=40, d_model=16):
    """[관전 포인트 1] 시퀀스 끝에서 만든 loss가 시퀀스 '맨 앞' 입력까지 얼마나 잘 전달되는가.
    RNN(순차 구조) vs Attention(직접 연결 구조)을 같은 조건에서 비교한다."""

    # --- RNN: 한 스텝씩 이전 은닉상태를 거쳐 전달 → 먼 과거일수록 tanh·가중치 곱이 누적된다 ---
    rnn = nn.RNN(input_size=d_model, hidden_size=d_model, num_layers=1, nonlinearity="tanh", batch_first=True)
    x_rnn = torch.randn(1, seq_len, d_model, requires_grad=True)
    _, hT = rnn(x_rnn)
    loss_rnn = hT.pow(2).sum()  # 시퀀스 '마지막' 은닉상태로만 loss를 만든다
    loss_rnn.backward()
    rnn_grad = x_rnn.grad.norm(dim=-1).squeeze(0).detach()  # (seq_len,) — 각 위치 입력이 받은 gradient 크기

    # --- Attention: 모든 위치가 서로 직접 연결(한 홉) → 거리와 무관하게 신호가 바로 전달된다 ---
    mha = nn.MultiheadAttention(embed_dim=d_model, num_heads=4, batch_first=True)
    x_attn = torch.randn(1, seq_len, d_model, requires_grad=True)
    out, _ = mha(x_attn, x_attn, x_attn)
    loss_attn = out[:, -1, :].pow(2).sum()  # 마찬가지로 '마지막 위치의 출력'으로만 loss를 만든다
    loss_attn.backward()
    attn_grad = x_attn.grad.norm(dim=-1).squeeze(0).detach()

    return rnn_grad, attn_grad


def parallelization_experiment(seq_len=200, d_model=64, batch=32):
    """[관전 포인트 2] 구조적으로 '순차 계산이 강제되는가 아닌가'가 처리 속도에 미치는 영향.
    RNNCell을 한 스텝씩 파이썬 루프로 도는 것(RNN 방식) vs 전체를 한 번의 행렬곱으로 처리하는 것
    (Transformer가 모든 위치를 한 번에 처리하는 구조와 같은 원리)을 비교한다."""
    rnn_cell = nn.RNNCell(d_model, d_model)
    linear = nn.Linear(d_model, d_model)
    x = torch.randn(batch, seq_len, d_model)

    h = torch.zeros(batch, d_model)
    t0 = time.perf_counter()
    with torch.no_grad():
        for t in range(seq_len):
            h = rnn_cell(x[:, t, :], h)  # 이전 스텝의 h가 있어야 다음을 계산할 수 있다 — 순서 강제
    t_sequential = time.perf_counter() - t0

    t0 = time.perf_counter()
    with torch.no_grad():
        _ = linear(x)  # 모든 위치를 동시에 — 위치 간 의존성이 없어 한 번의 연산으로 끝난다
    t_parallel = time.perf_counter() - t0

    return t_sequential, t_parallel


def plot_gradient_comparison(rnn_grad, attn_grad, filename="results/1.vanishing_gradient.png"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(rnn_grad.numpy(), color="#c0392b", marker="o", markersize=3, label="RNN")
    axes[0].plot(attn_grad.numpy(), color="#27ae60", marker="o", markersize=3, label="Attention")
    axes[0].set_xlabel("시퀀스 위치(0=맨 앞 과거, 끝=최근)")
    axes[0].set_ylabel("입력이 받은 gradient 크기")
    axes[0].set_title("선형 스케일 — RNN은 사실상 0으로 보인다")
    axes[0].legend()

    axes[1].semilogy(rnn_grad.numpy(), color="#c0392b", marker="o", markersize=3, label="RNN")
    axes[1].semilogy(attn_grad.numpy(), color="#27ae60", marker="o", markersize=3, label="Attention")
    axes[1].set_xlabel("시퀀스 위치(0=맨 앞 과거, 끝=최근)")
    axes[1].set_ylabel("입력이 받은 gradient 크기 (log 스케일)")
    axes[1].set_title("로그 스케일 — RNN이 얼마나 작은지 자릿수로 확인")
    axes[1].legend()

    plt.suptitle("시퀀스 끝에서 만든 loss가 '맨 앞' 입력까지 전달되는 정도\n"
                 "RNN: 과거로 갈수록 급격히 소실 / Attention: 거리와 무관하게 유지",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  RNN → Transformer 전환 배경: 기울기 소실 · 병렬화")
    print("=" * 60)

    print("\n[ 1. 기울기 소실(Vanishing Gradient) ]")
    print("-" * 40)
    seq_len = 40
    rnn_grad, attn_grad = vanishing_gradient_experiment(seq_len=seq_len)
    print(f"  시퀀스 길이: {seq_len}, loss는 '마지막 위치'의 출력으로만 계산")
    print(f"  RNN       — 맨 앞(t=0) gradient: {rnn_grad[0]:.2e}  |  맨 끝(t={seq_len-1}) gradient: {rnn_grad[-1]:.4f}")
    print(f"              비율(앞/끝): {(rnn_grad[0]/rnn_grad[-1]).item():.2e}  ← 사실상 0, 학습 신호가 안 옴")
    print(f"  Attention — 맨 앞(t=0) gradient: {attn_grad[0]:.4f}  |  맨 끝(t={seq_len-1}) gradient: {attn_grad[-1]:.4f}")
    print(f"              비율(앞/끝): {(attn_grad[0]/attn_grad[-1]).item():.4f}  ← 같은 자릿수, 신호가 살아있음")
    plot_gradient_comparison(rnn_grad, attn_grad)

    print("\n[ 2. 병렬화(Parallelization) ]")
    print("-" * 40)
    t_seq, t_par = parallelization_experiment()
    print(f"  순차 처리(RNN 방식, 200스텝 파이썬 루프): {t_seq*1000:.2f}ms")
    print(f"  병렬 처리(위치 무관, 한 번의 행렬곱):      {t_par*1000:.2f}ms")
    print(f"  배속: {t_seq/t_par:.1f}배")

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 기울기 소실이 왜 생기나:
   - RNN은 h_t = f(h_{t-1}, x_t) — 한 스텝의 정보가 다음 스텝으로 가려면 반드시 이전 스텝을
     "거쳐야" 한다. 40스텝 떨어진 과거의 gradient는 tanh 미분(항상 1보다 작음)과 가중치 곱을
     40번 반복해서 곱한 값이라 지수적으로 작아진다 — 위 실측에서 사실상 0(10^-14 수준)이었다.
   - Attention은 모든 위치가 QK^T로 "직접" 연결된다(몇 단계를 거치지 않고 한 번에). 그래서
     시퀀스가 아무리 길어도 먼 과거의 gradient가 거의 줄어들지 않는다.

2. 병렬화가 왜 중요한가:
   - RNN은 h_t를 계산하려면 h_{t-1}이 반드시 먼저 있어야 한다 — 구조적으로 한 스텝씩만
     계산 가능(파이썬 for 루프를 못 벗어난다).
   - Transformer는 각 위치의 계산(그리고 attention의 QK^T)이 서로를 "먼저 기다릴 필요"가
     없어 GPU에서 통째로 병렬 처리된다. 위 실측에서도 10배 넘게 차이났다(실행마다 조금씩
     달라질 수 있음 — 위 숫자를 직접 확인할 것). 실전 GPU·긴 시퀀스·큰 배치에서는 이 차이가
     훨씬 커진다.
   - 이게 "왜 대형 모델은 다 Transformer 계열인가"의 실질적 이유다 — 같은 학습 시간에
     RNN보다 훨씬 많은 데이터를 처리할 수 있다.

3. 그래서 Transformer가 대신 치른 대가:
   - `8.positional_encoding`에서 봤듯, 병렬 처리 대신 "순서 정보"를 스스로는 못 갖게 됐다
     → 그래서 위치 정보를 명시적으로 더해줘야 했다.
   - attention 계산량은 시퀀스 길이의 제곱에 비례한다(모든 쌍을 비교하므로) — 그래서 매우 긴
     문서에는 여전히 비용 문제가 있다(`12.kv_cache`가 그 비용을 조금이나마 줄이는 기법).
""")


if __name__ == "__main__":
    main()
