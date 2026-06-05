# pip install langchain langchain-ollama
#
# Ollama + LangChain 7: 도구 호출 에이전트.
# create_agent 가 "모델이 도구를 부를지/어떤 인자로 부를지" 자동 결정 → 실행 → 답변 루프를 돈다.
# ※ tool calling 을 지원하는 모델 필요(mistral · llama3.1 · qwen2.5 등).

from langchain_ollama import ChatOllama
from langchain.agents import create_agent

# 도구: 함수 + docstring 이 곧 모델이 읽는 명세
def word_length(word: str) -> int:
    """주어진 단어/문장의 글자 수를 센다."""
    return len(word)

llm = ChatOllama(model="mistral", temperature=0)

agent = create_agent(
    model=llm,
    tools=[word_length],
    system_prompt="너는 도구를 활용해 정확히 답하는 도우미다.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "'안녕하세요'는 몇 글자야? 도구를 써서 세어줘."}]
})
print(result["messages"][-1].content)
