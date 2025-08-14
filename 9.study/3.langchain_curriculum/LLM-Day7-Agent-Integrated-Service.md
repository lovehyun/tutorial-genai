# LLM 7일차: Agent를 통한 통합 서비스 (자체 GPT 지식 + Wiki 검색 + 웹 검색)

## 학습 목표
- 다양한 정보원(자체 지식베이스, Wikipedia, 웹 검색)을 **에이전트 도구**로 결합합니다.
- 사용자 질문에 따라 **적절한 소스**를 선택/결합하여 답변하는 통합 서비스 구현.

---

## 설치
```bash
pip install wikipedia langchain langchain-openai duckduckgo-search python-dotenv
```

---

## 도구 정의
```python
from langchain.tools import tool
import wikipedia
from duckduckgo_search import DDGS

# 자체 GPT 지식은 LLM 프롬프트에 내장

@tool
def wiki_search(query: str) -> str:
    """위키백과에서 검색하여 요약 반환"""
    try:
        wikipedia.set_lang("ko")
        results = wikipedia.summary(query, sentences=3)
        return results
    except Exception as e:
        return f"Wiki 검색 실패: {e}"

@tool
def web_search(query: str) -> str:
    """DuckDuckGo 웹 검색 결과 상위 요약"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        return "\n".join(f"{r['title']}: {r['body']}" for r in results)
    except Exception as e:
        return f"웹 검색 실패: {e}"
```

---

## 에이전트 구성
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [wiki_search, web_search]

SYSTEM = (
    "당신은 질문에 따라 자체 지식, Wiki 검색, 웹 검색을 선택해 답변하는 조력자입니다."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "{input}")
])

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

print(executor.invoke({"input": "서울의 역사적 유래를 알려줘"}))
print(executor.invoke({"input": "최신 인공지능 트렌드"}))
```

---

## 확장 아이디어
- 자체 지식베이스: RAG retriever를 도구로 추가
- 소스별 답변 신뢰도/출처 표기
- 결과 병합 후 LLM으로 재요약
