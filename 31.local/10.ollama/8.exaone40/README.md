# 8.exaone40 — EXAONE 4.0 의 새 기능: 생각 모드 · Tool Calling (Ollama)

**EXAONE 4.0**(LG AI Research, 2025)은 [`../7.exaone35`](../7.exaone35)(EXAONE 3.5)의 다음
세대다. 순수 한국어 활용은 7.exaone35 와 구조가 같으니, 여기서는 **3.5에는 없던 두 가지**만
다룬다 — 생각 모드(reasoning)와, 3.5의 가장 큰 약점이었던 **tool calling**.

## 핵심 개념부터

- **EXAONE 3.5**: tool calling 자체를 지원하지 않는다(`../7.exaone35/README.md`에 명시).
- **EXAONE 4.0**: LG 공식 발표에 agentic tool use, Function Calling, MCP 지원이 명시됐고,
  Non-reasoning/Reasoning 모드를 한 모델 안에서 통합했다(논문 제목 자체가 "Unified LLM
  Integrating Non-reasoning and Reasoning Modes") — Qwen 3.5(`../6.qwen35`)와 같은 하이브리드 구조다.

## ⚠️ 먼저 알아야 할 것 — 공식 라이브러리에 아직 없다

Qwen 3.5 와 달리 **EXAONE 4.0 은 Ollama 공식 라이브러리에 없다.** 커뮤니티가 올린 GGUF만
받을 수 있다 — 그리고 **어느 걸 받느냐에 따라 실제 동작이 완전히 다르다**(아래 실측 참고).
이 폴더는 두 커뮤니티 버전을 나란히 놓고 비교해서, "capability가 선언돼 있다"와 "실제로
동작한다"가 다른 문제라는 걸 실측으로 보여준다.

> **"GGUF가 뭐고 공식/커뮤니티 버전 차이가 뭔지, 왜 EXAONE만 공식이 없는지"**가 궁금하면
> → [`../0.gguf_and_open_weights.md`](../0.gguf_and_open_weights.md) 를 먼저 읽어볼 것.

```bash
ollama pull ingu627/exaone4.0:1.2b        # tool calling 실측 0/3 성공 — 비교용
ollama pull sam860/exaone-4.0:1.2b        # tool calling 실측 3/3 성공 — 예제 기본
pip install ollama
```

## 예제

| 파일 | 내용 |
|---|---|
| `1.reasoning_mode.py` | `think=True/False` 사용 + **`message["thinking"]`이 안 채워지고 `</think>` 태그가 본문에 그대로 새는 실제 문제**와 수동 파싱 대응 |
| `2.reasoning_mode_stream.py` | `stream=True`로 원본 스트림을 그대로 지켜보고, `</think>` 등장을 직접 감지해서 사고/답변을 실시간으로 나누기 |
| `3.tool_calling.py` | 같은 "EXAONE 4.0"인데 GGUF 업로더에 따라 tool calling이 **0/3 vs 3/3**으로 갈리는 실측 비교 |

## 관전 포인트 — "선언된 capability"와 "실제 동작"은 다르다

`ollama show`로 확인하면 `ingu627/exaone4.0:1.2b`와 `sam860/exaone-4.0:1.2b` 둘 다
`tools`·`thinking` capability가 똑같이 선언돼 있다. 그런데 실측하면:

| | ingu627/exaone4.0:1.2b | sam860/exaone-4.0:1.2b |
|---|---|---|
| tool calling (3회) | **0/3** (도구 호출 없이 날씨를 지어냄) | **3/3** |
| `message["thinking"]` 분리 | 안 됨(`</think>` 태그가 본문에 섞임) | 안 됨(동일) |

**원인은 모델 가중치가 아니라 Ollama Modelfile 템플릿(업로더가 도구 스키마·생각 태그를
얼마나 정확히 설정했는가)이다.** 공식 라이브러리(Qwen 3.5)에는 없는, 커뮤니티 업로드 특유의
리스크 — "capability가 찍혀 있다"고 안심하지 말고 몇 번 실제로 호출해서 확인(smoke test)해야
한다는 게 이 폴더의 핵심 교훈이다.

## Qwen 3.5 와 무엇이 다른가

| | Qwen 3.5 (`../6.qwen35`) | EXAONE 4.0 (여기) |
|---|---|---|
| Ollama 배포 | 공식 라이브러리 | 커뮤니티 GGUF만 (업로더마다 품질 다름) |
| `message["thinking"]` | 정상 분리됨 | **분리 안 됨** — `</think>` 태그가 본문에 섞임 |
| tool calling | 안정적 (5/5) | 업로더에 따라 0/3 ~ 3/3 |
| 생각 모드 속도(GPU) | 31초(OFF 대비 4배) | 2.0초(OFF 2.3초와 거의 동일 — 1.2B라 원래 빠름) |
| 생각 모드가 끝을 맺는가 | 예산 부족 시 실패(빈 답변) | GPU 실측에서 아예 문장이 끊긴 채 끝난 경우 있음 |

## 다음 단계
- 순수 한국어 응용(대화·요약·구조화출력·RAG) → [`../7.exaone35`](../7.exaone35)
- 같은 "생각 모드 + tool calling" 조합을 공식 라이브러리 모델로 먼저 보고 싶다면 → [`../6.qwen35`](../6.qwen35)
