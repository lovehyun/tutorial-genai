# 10.web_visualizations — 브라우저에서 바로 만져보는 종합 데모

`1.transformer` ~ `11.training_objectives`가 각 개념을 **개별적으로** Python 스크립트로 파고든
자리였다면, 여기는 그 개념들의 **종합/시각화 버전**을 브라우저에서 바로 조작해보는 자리다.
설치도 서버도 필요 없다 — HTML 파일을 더블클릭해서 열면 끝난다.

## 폴더

| 폴더 | 종합하는 내용 | 실행 |
|---|---|---|
| [`1.transformer_full/`](1.transformer_full/) | 토큰화·임베딩·어텐션·학습·생성 — 미니 Transformer를 순수 JS로 밑바닥부터 구현 | HTML 파일 열기 |
| [`2.positional_encoding/`](2.positional_encoding/) | `8.positional_encoding/`의 sin/cos 인코딩 — 슬라이더로 실시간 재계산 | HTML 파일 열기 |
| [`3.decoding_strategies/`](3.decoding_strategies/) | `9.decoding_strategies/`의 temperature/top-k/top-p — 실측 GPT-2 데이터로 실시간 재계산 | HTML 파일 열기 |

## 왜 파이썬 버전과 따로 있나

파이썬 버전(`matplotlib`)은 "실행해서 결과 이미지를 본다"는 한 방향 흐름이다. 여기 웹 데모는
**슬라이더를 움직이며 값이 바뀌는 걸 실시간으로** 본다 — 예를 들어 `2.positional_encoding`에서
"차원 수를 늘리면 패턴이 어떻게 촘촘해지는지"를 코드를 다시 실행하지 않고 바로 확인할 수 있다.
같은 개념을 "정적 결과"(파이썬)와 "실시간 조작"(웹) 양쪽으로 보면 이해가 더 단단해진다.

## 실행

브라우저(Chrome/Edge 등)로 각 폴더의 `.html` 파일을 그냥 열면 된다. 별도 설치·서버 불필요 —
전부 순수 HTML/CSS/JavaScript로만 만들어졌다.

> ⚠️ 이 폴더의 JS 로직(포지셔널 인코딩 계산, softmax/top-k/top-p 필터링)은 Node.js로 단위
> 테스트해서 수치적으로는 검증했지만, 브라우저 렌더링(캔버스 그림·레이아웃)까지 직접 눈으로
> 확인하지는 못했다 — 실행 환경에 GUI 브라우저가 없어서다. 열어보고 이상이 있으면 알려줄 것.

## 다음 단계
- 순수 Python 버전과 비교 → [`../8.positional_encoding/`](../8.positional_encoding/), [`../9.decoding_strategies/`](../9.decoding_strategies/)
