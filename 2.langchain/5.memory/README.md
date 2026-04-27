# 대화 메모리

LangChain의 메모리 시스템으로 대화 히스토리를 관리하는 예제입니다.

## 핵심 개념

### 메모리가 필요한 이유
LLM API는 기본적으로 **무상태(stateless)** — 매 호출마다 이전 대화를 기억하지 못합니다.
메모리 시스템으로 이전 대화를 함께 전달하여 문맥을 유지합니다.

### 메모리 유형
| 유형 | 설명 |
|------|------|
| `ConversationBufferMemory` | 전체 대화를 그대로 저장 (구버전) |
| `ConversationSummaryMemory` | 대화를 요약하여 저장 (토큰 절약) |
| `RunnableWithMessageHistory` | LCEL 기반 메모리 (신버전) |
| LangGraph 메모리 | `MemorySaver` 체크포인팅 (최신) |

## 예제 목록

| 파일 | 설명 |
|------|------|
| `0.langchain_review.py` | LangChain 기본 복습 |
| `1.1_nomemory.py` | 메모리 없는 기본 상태 (비교용) |
| `1.2_nomemory2_chatbot_cli.py` | 메모리 없는 CLI 챗봇 |
| `2.1_memory_old.py` | 구버전 메모리 API |
| `2.2_memory_old2_savecnt.py` | 구버전 메모리 (저장 횟수 제한) |
| `3.1~3.4` | 신버전 메모리 (파일, SQLite 저장) |
| `4.1~4.3` | 히스토리 관리 (세션, 세션 카운트) |
| `5.2~5.4` | 히스토리 요약 + 챗봇 CLI |
| `6.1~6.2` | 대화 요약 메모리 (구/신 버전) |
| `7.1_langgraph_memory.py` | LangGraph 기반 메모리 |
| `7.2_langgraph_memory2_summary.py` | LangGraph 요약 메모리 |

## 학습 순서

1. **기초**: 메모리 없는 상태 이해 (1번)
2. **구버전**: ConversationBufferMemory (2번)
3. **신버전**: RunnableWithMessageHistory (3~5번)
4. **요약**: 대화 요약 메모리 (6번)
5. **최신**: LangGraph MemorySaver (7번)

## 실행

```bash
pip install langchain langchain-openai python-dotenv
python 1.1_nomemory.py
```
