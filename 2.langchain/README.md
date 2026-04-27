# LangChain 예제

LangChain 프레임워크를 활용한 LLM 애플리케이션 개발 예제입니다.

## 학습 순서

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.llm_models/` | LLM 모델 | OpenAI 모델 연동 (Completion, Chat, Flask) |
| `2.prompts/` | 프롬프트 | PromptTemplate, ChatPromptTemplate, 작업별 예제 |
| `3.structured_output/` | 구조화 출력 | StrOutputParser, Pydantic, with_structured_output |
| `4.chaining/` | 체이닝 | LCEL, RunnableLambda, RunnablePassthrough |
| `5.memory/` | 메모리 | 대화 히스토리 관리 (구버전/신버전) |
| `6.RAG/` | RAG | 문서 검색 + LLM 응답 생성 파이프라인 |
| `7.agents/` | 에이전트 | 도구 사용 자율 에이전트 (검색, 위키, 커스텀) |
| `8.langgraph/` | LangGraph | 상태 기반 그래프 워크플로우 |

## 사전 준비

```bash
pip install langchain langchain-openai langchain-community python-dotenv
```
