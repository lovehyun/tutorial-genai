# LangChain 에이전트

LLM이 도구를 자율적으로 사용하여 작업을 수행하는 에이전트 예제입니다.

## 핵심 개념

### 에이전트란?
LLM이 주어진 질문에 대해 **어떤 도구를 사용할지 스스로 판단**하고, 도구의 결과를 바탕으로 최종 답변을 생성하는 시스템입니다.

### Tool Calling Agent (최신 방식)
```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "질문"})
```

## 예제 목록

| 시리즈 | 설명 |
|--------|------|
| `0.agent_cap.py` | 사용 가능한 도구 목록 확인 |
| `1.1_llmmath.py` | 수학 계산 에이전트 |
| `2.*_wikipedia*.py` | Wikipedia 검색 (기본, 한국어, 수학, 구조화 출력) |
| `3.*_arxiv_thesis*.py` | arXiv 논문 검색 (검색, 번역, 체이닝) |
| `4.*_customtools*.py` | 커스텀 도구 정의 (덧��, 정보 조회, Serper) |
| `5.*_humanagent*.py` | Human-in-the-loop 에이전트 |
| `6.*_decide*.py` | 다중 도구 선택 판단 |
| `7.*_googlesearch*.py` | Google 검색 에이전트 |
| `8.1_complex.py` | 복합 에이전트 |
| `9.*_smartagent*.py` | 스마트 라우팅 다중 에이전트 |
| `10.webscan_app/` | 웹 스캔 에이전트 앱 |

## 설치

```bash
pip install langchain langchain-openai langchain-community wikipedia arxiv google-api-python-client
```
