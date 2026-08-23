# 2.sdk — OpenAI SDK (openai 라이브러리)

[`../1.restapi/`](../1.restapi/)에서 raw HTTP로 확인한 것과 같은 일을,
공식 SDK로 하면 얼마나 짧아지는지 비교하며 배웁니다. 파라미터·표준/추론 모델 구분은
[`../1.restapi/README.md`](../1.restapi/README.md)를 먼저 보세요.

## 학습 흐름

### SDK 기초 — chat.completions
| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.sdk_old.py` | 구버전 SDK (v0.x) — 옛 코드 참고용 |
| `2.sdk_new.py` | 신버전 SDK (v1.x) — 현재 표준 |
| `3.sdk_params.py` | SDK 방식의 파라미터 전달 |
| `4.chat_multiturn.py` | 멀티턴 (클라이언트가 messages 누적) → [`../3.chatbot/2.history/`](../3.chatbot/2.history/)로 연결 |
| `5.chat_vision.py` | 이미지 입력 (Vision) 맛보기 → 본격 딥다이브는 [`../9.multimodal/1.vision/`](../9.multimodal/1.vision/) |

### SDK — Responses API — 번호를 10부터 새로 시작
Chat Completions 기반 SDK(1~5)와는 **완전히 다른 API 시리즈**라 번호 대역을 일부러
띄웠습니다(6~9 결번). `../1.restapi/`의 10~11단계와 같은 규칙입니다.

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `10.sdk_response.py` | SDK로 Responses API 기본 호출 — `response.output_text` 한 줄 (`1.restapi`의 10단계 SDK 버전) |
| `11.response_multiturn.py` | SDK + `previous_response_id` 체인 (`1.restapi`의 11단계·이 폴더 4단계와 비교) |
| `12.response_streaming.py` | Responses API 스트리밍(`stream=True`) — `event.type`으로 이벤트 구분 |
| `13.response_web_search.py` | 내장 도구 `web_search` — 모델이 직접 검색까지 수행 |

> 같은 멀티턴을 세 방식으로 비교할 수 있습니다:
> - `4.chat_multiturn.py` — chat.completions, 클라이언트 누적
> - `../1.restapi/11.restapi_response_chain.py` — Responses, raw HTTP
> - `11.response_multiturn.py` — Responses, SDK (**가장 간결**)

> `13.response_web_search.py`는 [`../7.function_calling/`](../7.function_calling/)과 다릅니다 —
> function_calling은 **내가 만든** 함수를 모델이 호출하도록 하는 것이고,
> web_search는 **OpenAI가 서버에서 실행해주는** 내장 도구입니다.

## 실행

```bash
pip install openai python-dotenv
python 1.sdk_old.py   # 1단계부터 순서대로
```

API 키는 상위 폴더의 `.env` 파일(`../.env`)에 설정합니다:
```
OPENAI_API_KEY=sk-...
```
