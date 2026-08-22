# 6.ollama2_sdk — Ollama 를 파이썬 SDK 로 (권장)

`ollama` 파이썬 라이브러리로 호출합니다. REST 의 URL/JSON/파싱을 라이브러리가 감춰줘서
**파이썬에서 가장 편한 방식**입니다. (내부적으론 같은 REST API 를 호출)

> 추상화 순서: **[REST](../6.ollama1_restapi) → SDK(여기) → [LangChain](../6.ollama3_langchain)**
> 핵심 1~3 은 REST 폴더와 **같은 코드의 비교쌍** 입니다 — `requests.post` 가 `ollama.chat` 한 줄로.

## 핵심 (REST 버전과 1:1 비교)

| 파일 | 내용 | REST 짝 |
|---|---|---|
| `1.chat.py` | 기본 채팅 (`ollama.chat`) | `../6.ollama1_restapi/1.chat.py` |
| `2.streaming.py` | 스트리밍 (`stream=True` for 루프) | `../6.ollama1_restapi/2.streaming.py` |
| `3.multiturn.py` | 멀티 턴 (히스토리 누적) | `../6.ollama1_restapi/3.multiturn.py` |

## 추가 예제 (SDK 응용)

| 파일 | 내용 |
|---|---|
| `4.wordchain.py` / `4.wordchain2_winner.py` | 끝말잇기 게임 (AI 와 대결, 승패 판정) |
| `5.storytelling.py` / `5.storytelling2_end.py` | 협업 스토리텔링 (이어쓰기, 종료 조건) |
| `twobots/` | 두 봇이 서로 대화하는 미니 앱 (HTTP 서버 2개) |

## 핵심 정리
- 같은 일을 REST 대비 **훨씬 짧게** — `pip install ollama` 후 `ollama.chat(...)`.
- 파이썬 프로젝트라면 보통 SDK 가 1순위. 다른 언어/원격 호출이면 REST.
- 더 높은 추상화(체인·메모리·툴·RAG)는 [`../6.ollama3_langchain`](../6.ollama3_langchain).

## 실행
```bash
pip install ollama
ollama pull qwen2.5:1.5b
python 1.chat.py
```
