# 13.rnn_vs_transformer — Transformer가 RNN을 대체한 이유

Transformer(2017) 이전엔 RNN/LSTM이 시퀀스 처리의 표준이었다. 왜 대체됐는지 두 가지를 직접
측정해서 확인한다 — ① 기울기 소실(먼 과거의 학습 신호가 전달 안 됨), ② 병렬화(RNN은 구조적으로
한 스텝씩만 계산 가능).

## 파일

| 파일 | 내용 |
|---|---|
| `1.rnn_vs_transformer.py` | ① RNN vs Attention의 gradient 전달을 실측 비교 ② 순차 처리 vs 병렬 처리 속도 실측 비교 |

## 실행 (실측 결과, `torch.manual_seed(0)`으로 재현 가능)
```bash
pip install torch matplotlib numpy
python 1.rnn_vs_transformer.py
```
```
[기울기 소실] 시퀀스 길이 40, loss는 마지막 위치에서만 계산
  RNN       — 맨 앞 gradient: 5.60e-14  |  맨 끝 gradient: 1.3476  (비율 4e-14 — 사실상 0)
  Attention — 맨 앞 gradient: 0.0045    |  맨 끝 gradient: 0.0218  (비율 0.21 — 같은 자릿수)

[병렬화] 200스텝
  순차 처리(RNN 방식): 8.53ms
  병렬 처리(Transformer 방식): 0.56ms  → 15배 차이
```

## 관전 포인트
- **기울기 소실 수치가 핵심**: RNN은 시퀀스 맨 앞 입력이 받는 학습 신호가 맨 끝의 **10^-14배**
  — 40스텝 동안 tanh 미분과 가중치 곱이 40번 반복되며 지수적으로 작아진 결과다. 이래서 RNN은
  "먼 과거를 기억 못 한다"는 문제가 구조적으로 생긴다. Attention은 모든 위치가 QK^T로 직접
  연결돼(몇 단계를 거치지 않고 한 번에) 거리와 무관하게 신호가 살아있다.
- **병렬화는 GPU 활용의 문제다** — RNN은 h_t 계산에 h_{t-1}이 반드시 먼저 있어야 해서 파이썬
  for 루프를 벗어날 수 없다. Transformer의 각 위치 계산(그리고 attention 자체도)은 서로를
  기다릴 필요가 없어 GPU가 한 번에 처리한다 — 대형 모델이 전부 Transformer 계열인 실질적 이유.
- **공짜는 없다** — 병렬 처리를 얻은 대신 RNN이 공짜로 갖고 있던 "순서 감각"을 잃었다(그래서
  `8.positional_encoding`이 필요했다), 그리고 attention 계산량은 시퀀스 길이의 제곱에 비례한다
  (`12.kv_cache`가 그 비용을 조금 줄이는 기법).

## 다음 단계
- 왜 순서 정보를 따로 넣어야 하는지 → [`../8.positional_encoding/`](../8.positional_encoding/)
- attention의 제곱 비용을 완화하는 기법 → [`../12.kv_cache/`](../12.kv_cache/)
