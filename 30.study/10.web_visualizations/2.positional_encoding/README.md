# 2.positional_encoding — 슬라이더로 만져보는 포지셔널 인코딩

`8.positional_encoding/1.pe_visualize.py`와 완전히 같은 sin/cos 공식을 쓰지만, matplotlib 정적
이미지 대신 **슬라이더로 위치 수·차원 수를 바꾸면 즉시 다시 그려진다**.

## 파일
| 파일 | 내용 |
|---|---|
| `1.pe_web_demo.html` | 히트맵/파형 두 가지 보기 모드, 위치 수·차원 수 실시간 조절 |

## 실행
브라우저로 `1.pe_web_demo.html`을 열면 된다. 설치 불필요.

## 관전 포인트
- **차원 수(d_model) 슬라이더를 올려보면** — 낮은 차원(왼쪽)의 촘촘한 줄무늬와 높은 차원(오른쪽)의
  넓은 줄무늬 대비가 더 뚜렷해진다. "차원마다 주파수가 다르다"는 말이 그림으로 바로 보인다.
- **파형 모드**로 바꾸면 몇 개 차원을 실제 sin/cos 곡선으로 겹쳐 보여준다 — 왜 이걸 "포지셔널
  *인코딩*"이 아니라 종종 "위치 *파동*"이라 부르는지 느낄 수 있다.
- 계산 로직(`positionalEncoding()`)은 Node.js로 단위 테스트해서 `1.pe_visualize.py`의 Python
  구현과 수치적으로 동일한 결과를 내는 걸 확인했다.

## 다음 단계
- Python 버전(수치 출력 + permutation invariance 증명) → [`../../8.positional_encoding/`](../../8.positional_encoding/)
