# 1.transformer_full — 미니 Transformer, 순수 JS로 밑바닥부터

라이브러리 없이 `Matrix`, `SimpleTransformer` 클래스를 직접 구현해 토큰화 → 임베딩 → attention
계산(softmax 포함) → 학습 루프 → 텍스트 생성까지 전 과정을 브라우저 안에서 돌린다. 이 30.study
폴더 전체에서 실질적으로 가장 "원리 그 자체"에 충실한 자료다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.webbased_v1.html` | 초기 버전 |
| `2.webbased_v2_full.html` | 확장 버전 — 더 많은 단계/시각화 포함 |

## 실행
브라우저로 `2.webbased_v2_full.html`(더 완성된 버전)을 열면 된다. 설치 불필요.

## 관전 포인트
- `7.attention/2.qkv_visualize.py`가 **사전학습된 BERT**에서 Q/K/V를 추출해 시각화했다면,
  여기는 **학습되지 않은 상태의 Transformer를 직접 만들어서** 같은 계산(QK^T→softmax→×V)이
  코드 몇 줄로 구현된다는 걸 보여준다 — "실제로 별게 없다"는 걸 체감하는 게 핵심.
- 학습 루프까지 포함돼 있어 — `11.training_objectives/`에서 본 "loss가 어디서 계산되는가"가
  실제 코드로 어떻게 구현되는지도 여기서 확인할 수 있다.

## 다음 단계
- 사전학습 모델의 실제 attention 값 시각화 → [`../../7.attention/`](../../7.attention/)
- 여기서 빠진 위치 정보 시각화 → [`../2.positional_encoding/`](../2.positional_encoding/)
