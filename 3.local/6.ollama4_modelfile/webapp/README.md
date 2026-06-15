# webapp — gemma4-korean 대화 웹앱 (입력 / 생각 / 답변)

`gemma4-korean` 과 대화하며 **추론 과정(생각)을 실시간 스트림**으로, **최종 답변은 별도 컬럼**으로
나눠 보여주는 최소 디자인 웹앱입니다.

```
① 입력        ② 생각(thinking 스트림)        ③ 답변(raw) / ④ 답변(md 렌더)
[질문 입력]    모델의 추론이 실시간으로        위: 원문 그대로
[보내기]       흘러나옴(흐린 글씨)             아래: 마크다운 렌더링 결과
```

## 동작 원리 — 왜 태그 파싱을 안 하나

gemma4 는 **진짜 reasoning 모델**이라 추론을 **네이티브 `thinking` 채널**로 따로 냅니다.
스트림 청크가 두 필드로 옵니다:

| 응답 필드 | 보내는 곳 |
|---|---|
| `message.thinking` | **② 생각** 컬럼 |
| `message.content` | **③/④ 답변** 컬럼 |

> 처음엔 `<think>`/`<answer>` **텍스트 태그**로 나누려 했지만, 모델이 추론 도중 태그를
> **본문에서 그냥 언급**("`<answer>`로 최종 답변 작성")하면 파서가 오인식해 깨졌습니다.
> 그래서 텍스트 태그를 버리고 **네이티브 채널**만 씁니다. 백엔드는 두 가지로 이를 보강합니다:
> 1. `think=True` — 추론을 thinking 채널로 **강제** (content 에 추론이 새지 않음)
> 2. 태그 지시 없는 **깨끗한 system** 을 런타임에 전달 (Modelfile 의 태그 SYSTEM 을 덮어씀)

## 구성

| 파일 | 역할 |
|---|---|
| `app.py` | Flask 백엔드 — `/chat` 에서 ollama 스트림을 NDJSON(`{col, text}`)으로 중계 |
| `static/index.html` | 3컬럼 레이아웃 (답변 컬럼은 raw/md 상하 분할) |
| `static/style.css` | 최소 스타일 + 마크다운 렌더 영역 |
| `static/app.js` | 스트림을 읽어 컬럼별 분배, 답변은 `marked` 로 md 렌더 |

## 실행

```bash
pip install flask ollama
ollama create gemma4-korean -f ../Modelfile.reasoning   # 아직 없으면

python app.py        # → http://localhost:5000
```

> 마크다운 렌더는 `marked`(CDN)를 씁니다. 오프라인이면 ④ 칸은 raw 그대로 표시(폴백)됩니다.
