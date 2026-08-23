# 10.langchain — Claude를 LangChain으로

지금까지는 `anthropic` SDK를 직접 썼습니다. 여기서는 `langchain-anthropic`의 `ChatAnthropic`으로
같은 걸 LangChain 생태계(프롬프트 템플릿, 메모리, RAG, LCEL 체인) 안에서 다룹니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.intro.py` | `ChatAnthropic` 기본 호출 |
| `2.prompttemplate.py` | `PromptTemplate` / `ChatPromptTemplate` |
| `3.chaining.py` | LCEL 체인 — `prompt \| llm \| parser` |
| `4.conversation.py` | 대화 기록 — `RunnableWithMessageHistory` |
| `5.textloader.py` | 문서 로드 + 청킹 — `TextLoader`, `CharacterTextSplitter` |
| `6.vectorstore.py` | 벡터스토어(Chroma) — 문서 검색 기초 |
| `7.complex.py` | 다단계 LCEL 파이프라인 — 주제→질문 생성→답변→요약을 체인으로 연결 |

## 참고

- `6.vectorstore.py`는 임베딩에 OpenAI를 쓰므로(`pip install chromadb langchain-chroma
  langchain-openai`) `OPENAI_API_KEY`도 함께 필요합니다 — LLM은 Claude, 임베딩은 OpenAI를 섞어
  쓰는 조합입니다.
- 본격적인 RAG(로더 여러 종류, 검색 모드, 하이브리드 검색 등)는
  [`../../2.langchain/7.RAG/`](../../2.langchain/7.RAG/)에서 더 깊게 다룹니다 — 여기는
  "Claude로도 이 정도는 된다"를 보여주는 입문 수준입니다.

## 설치

```bash
pip install langchain-anthropic langchain-core python-dotenv
pip install langchain-community langchain-text-splitters   # 5, 6번
pip install chromadb langchain-chroma langchain-openai      # 6번
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...` (+ 6번은 `OPENAI_API_KEY`도)
