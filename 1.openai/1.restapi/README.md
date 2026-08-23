# 1.restapi — REST API 직접 호출

가장 단순한 호출에서 시작해, **한 단계에 개념 하나씩** 더해가며
Chat Completions(`/v1/chat/completions`) → Responses(`/v1/responses`) 순으로 배웁니다.
SDK 없이 `requests`로 직접 호출해, HTTP 요청/응답이 실제로 어떻게 생겼는지 눈으로 봅니다.

## 학습 흐름

### Chat Completions (`/v1/chat/completions`)
| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.restapi_hello.py` | 최소 호출 — 응답 JSON 통째로 확인 |
| `2.restapi_content.py` | 답변(content)만 추출 + 역할(system/user/assistant) |
| `3.restapi_params.py` | 응답 조절 파라미터 (temperature 등) |
| `4.restapi_chat.py` | 함수화 + 예외 처리 + 대화형 입력 (REST 완성형) |

### Responses (`/v1/responses`, 신형 API) — 번호를 10부터 새로 시작
Chat Completions와는 **완전히 다른 API 시리즈**라 번호 대역을 일부러 띄웠습니다(5~9 결번).

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `10.restapi_response.py` | Responses 입문 — `input` 문자열 + `output[0].content[0].text` |
| `11.restapi_response_chain.py` | `previous_response_id`로 서버측 대화 이어가기 (기본 30일 저장) |

> Responses는 chat.completions와 달리 **서버가 대화 상태를 저장**해, 매번 messages를 다시 보낼 필요가 없습니다.
> 신규 OpenAI 기능(추론 모델·내장 도구 등)도 Responses 중심으로 제공됩니다.
> SDK로 같은 걸 훨씬 짧게 쓰는 법은 [`../2.sdk/`](../2.sdk/)에서 이어집니다 (SDK도 같은 방식으로 10번대에서 이어짐).

## 주요 파라미터

| 파라미터 | 설명 | 범위 |
|----------|------|------|
| `temperature` | 창의성 제어 | 0.0(정확) ~ 2.0(창의) |
| `top_p` | 확률 기반 토큰 선택 | 0.0 ~ 1.0 |
| `max_tokens` | 최대 응답 길이 | 모델에 따라 다름 |
| `frequency_penalty` | 같은 단어 반복 억제 | -2.0 ~ 2.0 |
| `presence_penalty` | 새 주제 도입 장려 | -2.0 ~ 2.0 |

## 표준 모델 vs 추론(reasoning) 모델

위 파라미터들이 **모든 모델에서 동작하는 것은 아닙니다.** 모델은 크게 두 종류로 나뉘며,
경계선은 "GPT-4o 전/후"가 아니라 **표준 모델인지 추론 모델인지**입니다.
(흔한 오해: `gpt-4o`는 추론 모델이 아니라 표준 모델입니다.)

### 표준 모델 — 파라미터 정상 지원
`gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-4o-mini`, `gpt-4.1` 등.
`temperature`, `top_p`, `frequency_penalty`, `presence_penalty`, `max_tokens` 를
모두 지원하며 실제로 동작합니다. 이 폴더의 예제는 전부 표준 모델(`gpt-4o-mini`) 기준입니다.

> 모델이 좋아지면서 실무에서는 기본값을 그대로 쓰는 경우가 많아졌지만,
> 파라미터가 무력화된 것은 아닙니다. (`frequency/presence_penalty`는 원래도 활용도가 낮은 옵션)

### 추론 모델 — sampling 파라미터 미지원
`o1`, `o3`, `o3-mini`, `o4-mini`, `GPT-5` 계열(reasoning) 등.
내부적으로 '생각(reasoning) 토큰'을 사용하므로 무작위성 노브 대신
**추론 강도 노브**(`reasoning_effort`)를 씁니다.

| 파라미터 | 표준 모델 | 추론 모델 |
|----------|-----------|-----------|
| `temperature` / `top_p` | 지원 | ❌ 기본값 1만 허용 (다른 값 → 400 에러) |
| `frequency_penalty` / `presence_penalty` | 지원 | ❌ 미지원 |
| `max_tokens` | 지원 | ❌ → `max_completion_tokens` 사용 |
| `reasoning_effort` (low/medium/high) | — | ✅ 추론 깊이 조절 |

➡️ [`../2.sdk/3.sdk_params.py`](../2.sdk/3.sdk_params.py)에서 `model`을 `o3-mini` 같은 추론 모델로 바꾸면
`temperature`·`max_tokens` 때문에 오류가 납니다. 추론 모델은 별도 주제로 다룹니다.
(Responses API는 추론 모델과 잘 맞물려 설계됐습니다 — 10·11단계 참고.)

## 실행

```bash
pip install requests python-dotenv
python 1.restapi_hello.py   # 1단계부터 순서대로 실행
```

API 키는 상위 폴더의 `.env` 파일(`../.env`)에 설정합니다:
```
OPENAI_API_KEY=sk-...
```
