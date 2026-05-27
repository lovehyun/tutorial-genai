# 대화 메모리 (Conversation Memory)

LangChain 의 대화 상태(이전 메시지) 관리 방법을 단계별로 학습.

## 폴더 구조 (역할별 분리)

```
6.memory/
├── 0.legacy(deprecated)/     ← 옛 ConversationBufferMemory 계열 (참고용)
├── 1.nomemory/                 ← 메모리 없는 상태 + LangChain 복습 (출발점)
├── 2.storage/                ← "어디에 저장?" — In-Memory / File / SQLite (+ 데이터 파일)
├── 3.sessions/               ← "사용자/대화별 분리" — RunnableWithMessageHistory
├── 4.compression/            ← "토큰 줄이기" — trim_messages / summary
├── 5.langgraph/              ← LangGraph MemorySaver (최신/프로덕션)
└── README.md
```

> **방침**
> - 현행 API (`RunnableWithMessageHistory`, `InMemoryChatMessageHistory`, `trim_messages`, LangGraph `MemorySaver`) 만 메인 폴더에 둠
> - 옛 `ConversationBufferMemory`, `ConversationSummaryBufferMemory` 등은 `0.legacy(deprecated)/` 에 격리
> - 폴더 번호 = 파일 번호 prefix 가 일치 (예: `2.storage/` 안의 파일은 `2.x_...py`)

## 학습 흐름

```
1.nomemory         ─ 메모리 없을 때 어떻게 되는가? (왜 필요한가)
       ↓
2.storage        ─ 어디에 저장할 것인가? (In-Memory / File / SQLite)
       ↓
3.sessions       ─ 여러 사용자/대화를 어떻게 분리? (session_id)
       ↓
4.compression    ─ 대화가 길어질 때 토큰 어떻게 줄이는가? (trim / summary)
       ↓
5.langgraph      ─ 최신: LangGraph 체크포인터로 통합 (프로덕션 권장)
```

## 메모리 API 정리

| API | 분류 | 권장도 | 사용처 |
|-----|------|-------|-------|
| `ConversationBufferMemory` 등 | ❌ Deprecated | 안 씀 | `0.legacy/` 만 참고 |
| `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` | ✅ 현행 LCEL | 일반적 | 대부분의 케이스 |
| `trim_messages` | ✅ 현행 LCEL | 토큰 절약 시 | 긴 대화 자동 컷 |
| `MemorySaver` (LangGraph) | ✨ 최신 | 프로덕션 추천 | 복잡한 에이전트 / 분기 |

## 메모리 압축 방식 비교

| 방식 | 폴더 | 작동 원리 | 장점 | 단점 |
|------|------|---------|------|------|
| **윈도우** | `0.legacy/1.buffer_window_memory.py` | 최근 N개만 유지 | 단순/빠름 | 토큰 단위 제어 X |
| **trim_messages** | `4.compression/4.1_trim_messages.py` | **토큰 한도 안으로 자르기** | 가장 가벼움 / 빠름 | 오래된 정보 손실 |
| **summary** | `4.compression/4.2~4.4_summary_*.py` | 오래된 메시지를 LLM 으로 요약 | 정보 보존 ↑ | LLM 추가 호출 비용 |
| **LangGraph + summary** | `5.langgraph/5.2_with_summary.py` | 체크포인트 + 자동 요약 | 통합 솔루션 | 학습 곡선 ↑ |

## 폴더별 파일 상세

### `1.nomemory/` — 메모리 없는 상태 & LangChain 복습
| 파일 | 설명 |
|------|------|
| `1.0_langchain_review.py` | LangChain 기본 복습 (메모리 학습 전 워밍업) |
| `1.1_nomemory.py` | 매 호출마다 컨텍스트 잃음 — 메모리 필요성 체감 |
| `1.2_nomemory_chatbot_cli.py` | 메모리 없는 챗봇 CLI (비교용) |

### `2.storage/` — 어디에 저장할까
| 파일 | 저장소 | 영속성 |
|------|-------|--------|
| `2.1_inmemory.py` | `InMemoryChatMessageHistory` | 프로세스 종료 시 사라짐 |
| `2.2_file.py` | `FileChatMessageHistory` (`history.json`) | 파일로 영속 |
| `2.3_sqlite.py` | `SQLChatMessageHistory` (`chat_history.db`) | DB 로 영속, 동시 접근 ↑ |
| `2.4_print_history_util.py` | 히스토리 보기 유틸 | 위 파일들 디버깅 |

> 예제 실행 시 `history.json`, `chat_history.db` 가 이 폴더에 생성됩니다 (`.gitignore` 처리됨)

### `3.sessions/` — 다중 사용자/대화 분리
| 파일 | 설명 |
|------|------|
| `3.1_history.py` | `RunnableWithMessageHistory` 기본 |
| `3.2_history_session.py` | `session_id` 별 격리 |
| `3.3_history_sessioncnt.py` | 세션마다 메시지 카운트 관리 |

### `4.compression/` — 토큰 압축
| 파일 | 방식 |
|------|------|
| `4.1_trim_messages.py` | **`trim_messages`** — 토큰 기준 자르기 (가장 가벼움, 신규 추가) |
| `4.2_summary_basic.py` | LLM 요약 기본 |
| `4.3_summary_session.py` | 요약 + 세션 |
| `4.4_summary_manual_token.py` | tiktoken 기반 수동 토큰 계산 + 요약 |
| `4.5_chatbot_cli.py` | 요약 + 토큰 관리 완전 CLI |

### `5.langgraph/` — 최신 (LangGraph 체크포인팅)
| 파일 | 설명 |
|------|------|
| `5.1_memory_saver.py` | `MemorySaver` 기본 (스레드 ID 기반 상태) |
| `5.2_with_summary.py` | MemorySaver + 자동 요약 |

### `0.legacy(deprecated)/` — 옛 API (참고용, 사용 금지)
| 파일 | 옛 API |
|------|--------|
| `1.buffer_window_memory.py` | `ConversationBufferWindowMemory` |
| `2.summary_buffer_memory.py` | `ConversationSummaryBufferMemory` |

## 관련 폴더

- [`../2.prompts/4.advanced/`](../2.prompts/4.advanced/) — **`MessagesPlaceholder`** 가 메모리의 핵심 빌딩 블록
- [`../4.chaining/`](../4.chaining/) — `RunnableWithMessageHistory` 는 LCEL Runnable
- [`../9.langgraph/`](../9.langgraph/) — LangGraph `MemorySaver` 의 본격 다루기
- [`../8.agents/`](../8.agents/) — 에이전트는 거의 항상 메모리가 필요

## 실행

```bash
pip install langchain langchain-openai langchain-community python-dotenv tiktoken

python "1.nomemory/1.1_nomemory.py"
python "2.storage/2.1_inmemory.py"
python "4.compression/4.1_trim_messages.py"   # 신규: trim_messages
python "5.langgraph/5.1_memory_saver.py"
```
