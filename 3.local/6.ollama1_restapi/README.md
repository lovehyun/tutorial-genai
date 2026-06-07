# 6.ollama1_restapi — Ollama 를 REST API 로 (저수준)

Ollama 서버의 **HTTP REST API** 를 `requests` 로 직접 호출합니다.
URL·JSON 을 손수 다루는 **가장 저수준** 방식이라 "내부에서 무슨 일이 일어나는지" 가 다 드러납니다.

> 추상화 순서: **REST(여기) → [SDK](../6.ollama2_sdk) → [LangChain](../6.ollama3_langchain)**
> 핵심 1~3 예제는 SDK 폴더에 **같은 코드의 SDK 버전**이 있어 나란히 비교할 수 있습니다.

## 핵심 (SDK 버전과 1:1 비교)

| 파일 | 내용 | SDK 짝 |
|---|---|---|
| `1.chat.py` | 기본 채팅 (POST /api/chat) | `../6.ollama2_sdk/1.chat.py` |
| `2.streaming.py` | 스트리밍 (NDJSON 줄 파싱) | `../6.ollama2_sdk/2.streaming.py` |
| `3.multiturn.py` | 멀티 턴 (히스토리 누적) | `../6.ollama2_sdk/3.multiturn.py` |

## 추가 예제 (REST 특화)

| 파일 | 내용 |
|---|---|
| `4.external.py` / `4.external2.py` | 원격 호스트의 Ollama 서버 호출 (IP 지정) |
| `rag/` | REST 로 임베딩/검색 붙인 간단 RAG |

## 핵심 정리
- REST 는 **언어 불문**(curl·JS·모바일 등 어디서나 같은 API 호출) — 그게 장점.
- 대신 URL/JSON/스트리밍 파싱을 직접 해야 함 → SDK 버전과 비교해 보면 차이가 한눈에.

## 실행
```bash
pip install requests
ollama serve            # 데몬 (보통 자동 실행)
ollama pull qwen2.5:1.5b
python 1.chat.py
```
