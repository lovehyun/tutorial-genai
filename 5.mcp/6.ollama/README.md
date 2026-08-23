# 6.ollama — 로컬 모델로 MCP 쓰기

`2.openai`, `3.anthropic`과 같은 자리의 세 번째 벤더 폴더 — 차이는 **API 키도 인터넷도 필요 없는
로컬 오픈웨이트 모델**이라는 것뿐이다.

| 폴더 | 내용 |
|---|---|
| [`1.agent_tool/`](1.agent_tool/) | `2.openai/1.agent_tool`, `3.anthropic/2.anthropic_api`와 대칭 구조 — 수동→키워드→로컬 LLM 자동 |

## 왜 이 폴더가 있나
MCP는 "어떤 LLM 클라이언트에서든 같은 서버를 재사용한다"는 게 핵심 가치다(레포 최상위 README).
그 가치는 상용 API(OpenAI·Anthropic)에서만이 아니라 **완전 무료·오프라인 로컬 모델**에서도
그대로 성립한다는 걸 보여주는 게 이 폴더의 역할이다.

## 설치
```bash
# https://ollama.com 설치 (또는 앱 실행 — 로컬 서버 자동 기동)
ollama pull qwen2.5:7b
pip install mcp ollama
```

## 다음 단계
- 다른 벤더와 비교 → [`../2.openai/`](../2.openai/), [`../3.anthropic/`](../3.anthropic/)
- LangChain으로 Ollama + MCP를 쓰고 싶다면 → `4.langchain/1.quickstart/1.agent.py`의
  `ChatOpenAI`를 `langchain_ollama.ChatOllama`로 바꾸면 나머지 코드는 그대로 동작한다
  (인터페이스 호환성은 `2.langchain/1.llm_models/3.1_ollama.py` 참고).
