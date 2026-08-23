# 8.positional_encoding — 순서 정보는 어떻게 들어가는가

`7.attention`에서 본 QK^T→softmax→×V 계산을 잘 보면, 그 어디에도 "몇 번째 토큰인지"가 없다.
Attention은 그 자체로 **순서에 무관**하다(permutation invariant) — 그래서 Transformer는 입력에
위치 정보를 명시적으로 더해준다. 그게 포지셔널 인코딩이다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.pe_visualize.py` | ① attention이 순서를 모른다는 걸 숫자로 직접 증명 ② sin/cos 포지셔널 인코딩 계산·시각화 ③ 위치 간 유사도(거리 정보) 확인 |

## 실행
```bash
pip install torch matplotlib numpy
python 1.pe_visualize.py
```
`results/`에 히트맵·파형·유사도 그림 3장이 저장된다.

## 관전 포인트
- **1번 실험이 핵심**: "cat sat mat"에서 "cat"의 attention 출력과, 순서만 뒤집은 "mat sat cat"에서
  "cat"의 attention 출력을 직접 비교하면 **완전히 똑같다** — 위치 정보가 전혀 없다는 걸 숫자로
  확인한다. RNN은 한 스텝씩 순서대로 처리해서 순서가 구조에 내장되지만, attention은 집합 연산이라
  그렇지 않다.
- **왜 sin/cos인가**: 차원마다 다른 주파수를 쓰면 위치 조합마다 고유한 패턴이 생긴다. 학습이
  필요 없어 미리 계산 가능하고, 훈련 때 못 본 긴 문장에도 그대로 확장된다.
- **유사도 그림**이 보여주는 것: 가까운 위치일수록 코사인 유사도가 높다 — "몇 번째"라는 절대
  위치뿐 아니라 "얼마나 떨어져 있는지"라는 상대 거리 정보도 함께 담긴다.
- 최신 모델(Llama/Qwen 등)은 RoPE라는 다른 방식을 주로 쓰지만(회전 변환으로 상대 위치를
  인코딩), "왜 위치 정보가 필요한가"라는 목적은 여기서 본 sin/cos 방식과 같다.

## 다음 단계
- 어텐션 계산 자체를 더 깊게 → [`../7.attention/`](../7.attention/)
- 이 위치 정보 위에서 다음 토큰을 어떻게 고르는지 → [`../9.decoding_strategies/`](../9.decoding_strategies/)
