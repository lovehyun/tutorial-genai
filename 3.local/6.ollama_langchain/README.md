# 6.ollama_langchain — Ollama + LangChain

`6.ollama` 는 raw `ollama` 라이브러리/REST 로 로컬 LLM을 직접 호출한다.
여기서는 같은 로컬 모델을 **LangChain** 으로 감싸 LCEL 체인·메모리·구조화출력·도구·RAG 까지 단계별로 다룬다.
외부 API 키 불필요 — 전부 로컬에서 돈다.

## 준비
```bash
pip install langchain langchain-ollama langchain-core langchain-chroma pydantic

ollama serve                  # 로컬 서버 (기본 localhost:11434)
ollama pull mistral           # 채팅/도구/구조화출력용
ollama pull nomic-embed-text  # RAG 임베딩용 (8.rag.py)
```

## 순서
| 파일 | 내용 |
|------|------|
| `1.intro.py` | ChatOllama 기본 호출 |
| `2.lcel_chain.py` | LCEL 체인 (`prompt \| llm \| parser`) |
| `3.streaming.py` | 스트리밍 출력 |
| `4.chat_prompt.py` | system/human 메시지 + ChatPromptTemplate |
| `5.memory.py` | 대화 메모리 (RunnableWithMessageHistory) |
| `6.structured_output.py` | 구조화 출력 (with_structured_output + Pydantic) |
| `7.tool_agent.py` | 도구 호출 에이전트 (create_agent) |
| `8.rag.py` | RAG (OllamaEmbeddings + Chroma) |

## 메모
- **도구 호출(7)·구조화 출력(6)** 은 그 기능을 지원하는 모델이 필요하다 (mistral · llama3.1 · qwen2.5 등).
- 모델을 바꾸려면 각 파일의 `ChatOllama(model="...")` 만 수정하면 된다.
- Ollama 서버가 떠 있어야 한다(`ollama serve`). 모델은 미리 `ollama pull` 로 받아둔다.
