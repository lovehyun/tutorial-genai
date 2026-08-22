# 9.exaone — EXAONE 3.5 로 할 수 있는 다양한 것들 (Ollama)

**EXAONE 3.5** = LG AI Research 가 만든 한국어 강한 오픈 LLM.
여기서는 Ollama 로 로컬 실행하며, 대화부터 추론·구조화출력·RAG 까지 **여러 활용**을 단계별로 봅니다.

> `8.korean_llm` 은 EXAONE 으로 '한국어 NLP 태스크(감정/NER/번역 등)' 를 다루고,
> 이 폴더는 '**EXAONE 으로 할 수 있는 다양한 응용**' 에 집중합니다.

## 준비

```bash
# 1) Ollama 설치 (https://ollama.com) 후 모델 받기
ollama pull exaone3.5          # 기본(7.8B). 가벼운 버전: ollama pull exaone3.5:2.4b
# 2) 파이썬 패키지
pip install ollama
# 3) Ollama 데몬이 떠 있어야 함 (보통 자동 실행, 아니면: ollama serve)
```
> 모든 예제 상단의 `MODEL = "exaone3.5:latest"` 를 받은 태그에 맞게 바꾸면 됩니다.

## 학습 순서

| 파일 | 활용 | 핵심 |
|---|---|---|
| `1.chat.py` | 기본 대화 | 단일/멀티 턴, 맥락 누적 |
| `2.reasoning.py` | 단계적 추론 | "단계별로 생각하기"(CoT)로 정답률 ↑ |
| `3.summarize.py` | 요약 | 길이/형식 통제, 낮은 temperature |
| `4.structured_json.py` | 구조화 출력 | `format="json"` 으로 JSON 강제 → 앱 연동 |
| `5.code_assistant.py` | 코드 생성/설명 | 코딩 보조, 낮은 temperature |
| `6.streaming.py` | 스트리밍 | 토큰 실시간 수신 (SDK `stream=True` for 루프) — 챗봇 UX |
| `7.rag.py` | 간단 RAG | 문서 근거로만 답(할루시네이션 ↓) |

## 핵심 정리
- 호출은 **ollama 파이썬 SDK**(`ollama.chat` / `ollama.generate`) — REST 보다 간단. messages 구조는 OpenAI 와 유사. (REST vs SDK 비교: [`../6.ollama1_restapi`](../6.ollama1_restapi) ↔ [`../6.ollama2_sdk`](../6.ollama2_sdk))
- 작업별 권장: 추론=CoT프롬프트+temp0 / 요약·코드=낮은 temp / 구조화=`format=json` / 챗봇=streaming.
- EXAONE 은 **비상업 라이선스** — 상업적 사용 시 라이선스 확인 필요.
- ⚠️ **EXAONE 3.5 는 네이티브 tool calling(함수호출)을 지원하지 않습니다** (Ollama capability = `completion` 만).
  그래서 이 폴더엔 agent/도구사용 예제가 없습니다. **agent 가 필요하면 `tools` 지원 모델**
  (Qwen2.5 / Mistral)을 쓰세요 — 예: [`../6.ollama3_langchain/7.tool_agent.py`](../6.ollama3_langchain/7.tool_agent.py).
- 본격 벡터검색 RAG·LangChain 연동은 [`../../2.langchain/7.RAG`](../../2.langchain/7.RAG) 참고.
