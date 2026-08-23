# 3.decoding_strategies — 슬라이더로 만져보는 temperature / top-k / top-p

`9.decoding_strategies/1.decoding_visualize.py`가 실제로 GPT-2에서 뽑은 logit 값을 **그대로
가져와서**, temperature·top-k·top-p를 슬라이더로 바꿔가며 확률 분포가 실시간으로 재계산되는
걸 본다. 🎲 버튼으로 그 분포에서 직접 샘플링도 해볼 수 있다.

## 파일
| 파일 | 내용 |
|---|---|
| `1.decoding_web_demo.html` | "The capital of France is ___"의 실측 GPT-2 상위 15개 후보 + temperature/top-k/top-p 슬라이더 + 샘플링 버튼 |

## 실행
브라우저로 `1.decoding_web_demo.html`을 열면 된다. 설치 불필요.

## 관전 포인트
- **데이터가 진짜다** — 하드코딩된 예시가 아니라 `1.decoding_visualize.py` 실행으로 뽑은 실제
  GPT-2 logit 15개를 그대로 박아넣었다. 그래서 "1등이 Paris가 아니라 the"라는, 실제로 확인된
  소형 모델의 한계가 여기서도 똑같이 재현된다.
- ⚠️ 단, 이 데모는 상위 15개 후보로만 정규화한다(원래는 5만 개 넘는 전체 어휘로 정규화) — 그래서
  퍼센트 절댓값은 Python 스크립트의 실제 출력과 다르다. **상대적 비율과 슬라이더 효과**가 핵심.
- **top-k와 top-p를 각각 켜보면** — top-k는 항상 정해진 개수만 초록색(허용)으로 남고, top-p는
  분포가 뾰족한지 평평한지에 따라 남는 개수가 달라진다. 슬라이더를 함께 움직이며 두 방식의
  차이를 직접 비교해볼 것.
- 계산 로직(softmax, top-k/top-p 필터링)은 Node.js로 단위 테스트해서 정규화 합이 1.0이 되는지,
  top-k=5가 정확히 5개만 남기는지, top-p 컷오프가 누적확률 기준으로 정확히 동작하는지 확인했다.

## 다음 단계
- Python 버전(그래프 3종 + 학습 포인트 정리) → [`../../9.decoding_strategies/`](../../9.decoding_strategies/)
