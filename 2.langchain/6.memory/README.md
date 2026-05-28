# 대화 메모리 (Conversation Memory)

LangChain 의 대화 상태(이전 메시지) 관리 방법을 단계별로 학습합니다.

각 폴더는 **메모리가 풀어야 할 한 가지 문제**에 집중합니다.

## 폴더 구조

```
6.memory/
├── 0.legacy(deprecated)/    ← 옛 ConversationBufferMemory 계열 (블로그 참조용)
├── 1.nomemory/              ← 출발점: LangChain 복습 + 메모리 없으면 어떻게 되나
├── 2.storage/               ← "어디에 저장?" — InMemory / File / SQLite
├── 3.sessions/              ← "여러 사용자 분리" — RunnableWithMessageHistory
├── 4.compression/           ← "토큰 줄이기" (단기) — trim_messages / 자동 요약
├── 5.long_term/             ← "세션 간 영속" (장기) — 사용자 프로필 추출
├── 6.langgraph/             ← 최신: LangGraph MemorySaver (프로덕션 통합)
├── 7.web_app/               ← Flask 응용 — 메모리 기능을 웹으로 빌드업
└── README.md
```

> **방침**
> - 현행 API (`RunnableWithMessageHistory`, `InMemoryChatMessageHistory`, `trim_messages`, LangGraph `MemorySaver`) 만 메인에 둠.
> - 옛 `ConversationBufferMemory`, `ConversationSummaryBufferMemory` 등은 `0.legacy(deprecated)/` 에 격리 (구버전 블로그 참조용).
> - 폴더 번호 = 파일 번호 prefix. (예: `2.storage/` 안의 파일은 `2.x_...py`)
> - 모든 예제는 **chat 모델** (`ChatOpenAI` + `gpt-4o-mini`) 기반.

## 학습 흐름 — 어떤 문제를 푸는가

```
1.nomemory      ─ "메모리 없으면 이전 발화를 못 기억함" 을 체감 (+ 빠른 LangChain 복습)
       ↓
2.storage       ─ "어디에 저장하나?"          ← InMemory / File / SQLite
       ↓
3.sessions      ─ "여러 사용자를 어떻게 분리?" ← RunnableWithMessageHistory + session_id
       ↓
4.compression   ─ "대화가 길어지면 토큰 한도?"   ← trim_messages / 자동 요약 (단기)
       ↓
5.long_term     ─ "세션을 가로질러 기억하려면?" ← 사용자 프로필 추출 + 영속 (장기)
       ↓
6.langgraph     ─ "복잡한 워크플로우용 통합"     ← LangGraph MemorySaver
       ↓
7.web_app       ─ "지금까지 배운 메모리를 Flask 웹으로 빌드업"
```

## 메모리 API 정리

| API | 분류 | 권장도 | 사용처 |
|-----|------|-------|-------|
| `ConversationBufferMemory` 류 | ❌ Deprecated | 안 씀 | `0.legacy/` 참조용 |
| `InMemoryChatMessageHistory` + 수동 누적 | ✅ Low-level | 학습용 | 메모리 내부 흐름 이해 |
| `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` | ✅ 현행 LCEL | 일반 케이스 | 대부분 |
| `trim_messages` | ✅ 현행 LCEL | 토큰 절약 시 | 긴 대화 자동 컷 (단기) |
| 사용자 프로필 추출 + JSON/DB | ✅ 패턴 | 거의 모든 챗봇 | **세션 간 영속 (장기)** |
| `MemorySaver` (LangGraph) | ✨ 최신 | 프로덕션 추천 | 복잡한 에이전트 / 분기 |

## 메모리 압축 방식 비교

| 방식 | 폴더 | 작동 원리 | 장점 | 단점 |
|------|------|---------|------|------|
| **윈도우 (개수)** | `3.sessions/3.3_history_window.py` | 최근 N 턴만 유지 | 단순/빠름 | 토큰 단위 제어 X |
| **trim_messages** | `4.compression/4.1_trim_messages.py` | **토큰 한도 안으로 자르기** | 가장 가벼움 / 빠름 | 오래된 정보 손실 |
| **자동 요약** | `4.compression/4.2 ~ 4.4` | 오래된 메시지를 LLM 으로 요약 | 정보 보존 ↑ | LLM 추가 호출 비용 |
| **LangGraph + 요약** | `6.langgraph/6.2_with_summary.py` | 체크포인트 + 자동 요약 | 통합 솔루션 | 학습 곡선 ↑ |

---

## 폴더별 파일 상세

### `1.nomemory/` — 출발점

| 파일 | 설명 |
|------|------|
| `1.1_langchain_review.py` | **빠른 복습** — LCEL 파이프 + `MessagesPlaceholder` (메모리의 핵심 빌딩 블록) |
| `1.2_nomemory.py` | 메모리 없는 챗봇 — 매 호출이 독립적이라 이전 발화를 못 기억함을 체감 |

### `2.storage/` — 어디에 저장하나

> 이 폴더는 **저장소 자체** 만 봅니다. (자동화는 3 에서, 압축은 4 에서)
> 모든 파일이 동일 패턴 — **storage 객체 한 줄만 다름**.

| 파일 | 저장소 | 영속성 |
|------|-------|--------|
| `2.1_inmemory.py` | `InMemoryChatMessageHistory` | 프로세스 종료 시 사라짐 |
| `2.2_file.py` | `FileChatMessageHistory` (`history.json`) | 파일로 영속 |
| `2.3_sqlite.py` | `SQLChatMessageHistory` (`chat_history.db`) | DB 로 영속, 동시 접근 ↑ |
| `2.4_print_history_util.py` | `history.json` 한글 보기 (디버깅) | `\uXXXX` escape 풀어서 출력 |

> `history.json`, `chat_history.db` 는 실행 시 생성됩니다 (`.gitignore` 처리됨).

### `3.sessions/` — 다중 사용자 분리

| 파일 | 설명 |
|------|------|
| `3.1_history.py` | `RunnableWithMessageHistory` 기본 (단일 세션, 자동 누적) |
| `3.2_history_session.py` | `session_id` 별 격리 — 여러 사용자 동시 대응 |
| `3.3_history_window.py` | 세션 + 슬라이딩 윈도우 (최근 N 턴만 유지) |

### `4.compression/` — 토큰 압축

| 파일 | 방식 |
|------|------|
| `4.1_trim_messages.py` | **`trim_messages`** — 토큰 한도로 자르기 (LangChain 빌트인, **실무 권장**) |
| `4.2_summary_basic.py` | 자동 요약 (단일 세션) |
| `4.3_summary_session.py` | 자동 요약 + 멀티세션 격리 |
| `4.4_summary_manual_token.py` | tiktoken 으로 직접 토큰 계산 (참고 — 4.1 권장) |
| `4.5_chatbot_cli.py` | **종합 응용** — 자동 요약 챗봇 CLI |

### `5.long_term/` — 세션을 가로질러 영속하는 장기 메모리

지금까지 (1~4) 는 **한 세션 안의** 메모리 (= short-term) 였습니다.
실서비스에선 **세션이 끝나도 사용자를 기억** 해야 합니다 (이름·취미·과거 대화 등).
이걸 long-term memory 라고 합니다.

| 파일 | 설명 |
|------|------|
| `5.1_user_profile.py` | 대화 끝에 LLM 으로 사용자 정보 추출 → `profile.json` 영속 → 다음 실행 시 자동 로드 |
| `5.2_short_plus_long.py` | **short-term(history) + long-term(profile)** 을 한 체인에 결합하는 정석 패턴 |

> 두 파일은 **5.1 → 5.2 순서로 실행**하세요. 5.1 이 `profile.json` 을 만들고 5.2 가 그걸 사용합니다.

### `6.langgraph/` — 최신 (LangGraph 체크포인팅)

| 파일 | 설명 |
|------|------|
| `6.1_memory_saver.py` | `MemorySaver` 기본 (thread_id 기반 상태) |
| `6.2_with_summary.py` | `MemorySaver` + 자동 요약 통합 |

### `7.web_app/` — Flask 응용 (단계적 빌드업)

지금까지 배운 메모리 패턴을 Flask 웹으로 실제로 돌려봅니다.
**`chain`, `chatbot`, `get_session_history`** 등 핵심 이름을 그대로 유지하면서 단계적으로 확장 — `diff` 로 보면 무엇이 추가됐는지 한눈에 보입니다.

| 폴더 | 무엇 | 추가된 것 |
|------|------|----------|
| `1.single_chat/` | 단일 사용자 채팅 | `Flask + InMemoryChatMessageHistory` |
| `2.multi_user/` | 사용자별 분리 | + 로그인 / `sessions: dict[username, History]` |
| `3.conversations/` | 여러 대화 + 새 대화 / 이전 대화 보기 | + `SQLChatMessageHistory` (영속) + 사이드바 |

각 폴더 구조:
```
N.이름/
├── app.py                 # Flask 진입점
├── templates/
│   ├── login.html         # (#2, #3 만)
│   └── chat.html
└── static/style.css       # CSS 분리 (없어도 시맨틱 HTML 로 읽힘)
```

실행:
```bash
pip install flask langchain langchain-community langchain-openai sqlalchemy python-dotenv
python 1.single_chat/app.py      # → http://localhost:5001
python 2.multi_user/app.py       # → http://localhost:5002
python 3.conversations/app.py    # → http://localhost:5003
```

### `0.legacy(deprecated)/` — 옛 API (블로그 참조용)

`OpenAI` + `gpt-3.5-turbo` 시절의 옛 메모리 발전사.
**새 코드에는 쓰지 마세요.** 옛 자료를 읽을 때 매핑용으로만.

| 파일 | 옛 API | 현행 대체 |
|------|--------|---------|
| `0.buffer_memory.py` | `ConversationBufferMemory` (가장 원형) | `2.storage/2.1_inmemory.py` |
| `1.buffer_window_memory.py` | `ConversationBufferWindowMemory` | `3.sessions/3.3_history_window.py` |
| `2.summary_buffer_memory.py` | `ConversationSummaryBufferMemory` | `4.compression/4.1_trim_messages.py` 또는 `4.2~` |

## 자주 묻는 질문 (FAQ)

**Q. InMemory 저장량 한도는?**
→ 자료구조는 무제한(RAM). 단 프로세스 종료 시 사라짐 → 영속이 필요하면 `2.2 (File)` / `2.3 (SQLite)`.

**Q. 대화가 길어져 모델 컨텍스트 한도를 넘으면?**
→ 호출 실패. → `4.compression/` 에서 trim 또는 요약으로 해결.

**Q. 여러 사용자가 동시에 쓰면 메모리가 섞이지 않나?**
→ `2.storage/` 의 패턴은 단일 메모리라 섞임. → `3.sessions/` 의 `session_id` 분리로 해결.

**Q. 사용자가 다음 날 다시 와도 이름·취미를 기억하게 하려면? (long-term)**
→ `5.long_term/` 의 패턴 — 대화에서 사실을 LLM 으로 추출해 `profile.json`/DB 에 영속 저장 후,
   새 세션 시작 시 system prompt 에 주입.

**Q. 옛 코드의 `ConversationBufferMemory` 는 어떻게 바꿔야 하나?**
→ `0.legacy/0.buffer_memory.py` ↔ `2.storage/2.1_inmemory.py` 비교.
   대부분의 경우 `RunnableWithMessageHistory` (`3.sessions/3.1`) 로 대체.

## 관련 폴더

- [`../2.prompts/4.advanced/`](../2.prompts/4.advanced/) — `MessagesPlaceholder` 가 메모리의 핵심 빌딩 블록
- [`../4.chaining/`](../4.chaining/) — `RunnableWithMessageHistory` 는 LCEL Runnable
- [`../9.langgraph/`](../9.langgraph/) — LangGraph `MemorySaver` 본격적으로
- [`../8.agents/`](../8.agents/) — 에이전트는 거의 항상 메모리가 필요

## 실행

```bash
pip install langchain langchain-openai langchain-community python-dotenv tiktoken

python "1.nomemory/1.2_nomemory.py"
python "2.storage/2.1_inmemory.py"
python "3.sessions/3.2_history_session.py"
python "4.compression/4.1_trim_messages.py"
python "5.long_term/5.1_user_profile.py"
python "6.langgraph/6.1_memory_saver.py"

# Flask 웹 응용 (단계적 빌드업)
python "7.web_app/1.single_chat/app.py"
python "7.web_app/2.multi_user/app.py"
python "7.web_app/3.conversations/app.py"
```
