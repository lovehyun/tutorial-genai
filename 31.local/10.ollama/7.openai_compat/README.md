# 7.openai_compat — Ollama를 OpenAI 형태로 호출하기(드롭인 호환)

Ollama는 자체 REST(`1.restapi`)·SDK(`2.sdk`) 말고도 **OpenAI와 똑같은 형태의 엔드포인트**
(`/v1/chat/completions`)를 함께 제공한다. `base_url`만 로컬로 바꾸면 `openai` 파이썬 패키지를
그대로 재사용할 수 있다 — 이 저장소의 `1.openai/` 예제 코드가 사실상 그대로 로컬 모델에 붙는다.

## 파일
| 파일 | 내용 |
|---|---|
| `1.basic_chat.py` | `openai.OpenAI(base_url="http://localhost:11434/v1")`로 기본 채팅 |
| `2.swap_openai_ollama.py` | **같은 호출 함수**로 실제 OpenAI ↔ 로컬 Ollama를 나란히 비교 |

## 실행 (실측)
```bash
pip install openai python-dotenv
ollama pull qwen2.5:7b
python 1.basic_chat.py
python 2.swap_openai_ollama.py
```
```
질문: MCP가 뭔지 한 문장으로 설명해줘.

[OpenAI]      MCP는 'Microsoft Certified Professional'의 약자로 ...
[Ollama(로컬)] MCP는 마이크로소프트 공인 전문가(Microsoft Certified Professional)를 의미합니다.
```

## 관전 포인트
- **`base_url`/`api_key`/`model` 세 줄만 다르고 나머지 호출 코드는 완전히 동일** — 이게 이
  폴더의 요점이다. `1.openai/1.restapi`·`1.openai/2.sdk`에서 만든 함수를 그대로 갖다써도 된다.
- `api_key="ollama"`는 실제로 검사되지 않는 더미 값이다 — Ollama는 인증을 안 하지만 `openai`
  라이브러리가 값 자체는 요구해서 아무 문자열이나 넣는다.
- **실측 결과가 보여주는 진짜 함정**: API 형태가 같다고 지식/성능까지 같아지지 않는다.
  위 실행 결과에서 OpenAI·Ollama 둘 다 "MCP"를 엉뚱하게 해석했다(Microsoft Certified
  Professional) — 맥락 없는 약어는 모델 크기와 무관하게 틀릴 수 있다는 걸 직접 확인한 사례.
- **실전 활용**: 개발 중엔 무료·오프라인 로컬 모델로 반복 테스트하다가 배포 시에만 실제 API로
  바꾸는 식의 비용 절감 패턴, 또는 그 반대(민감한 데이터는 로컬, 고품질이 필요할 때만 API).

## 다음 단계
- 저수준 REST/SDK 호출과 비교 → [`../1.restapi/`](../1.restapi/), [`../2.sdk/`](../2.sdk/)
- 이 방식으로 MCP 도구도 호출할 수 있다 → [`../../../5.mcp/6.ollama/`](../../../5.mcp/6.ollama/)
  (거기서도 Ollama의 tool calling이 OpenAI 형식을 그대로 따른다는 걸 확인했다)

## 설치
```bash
pip install openai python-dotenv
```
