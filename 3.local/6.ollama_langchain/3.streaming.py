# pip install langchain-ollama
#
# Ollama + LangChain 3: 스트리밍.
# .stream() 은 토큰 조각(AIMessageChunk)을 순서대로 내준다.

from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")

for chunk in llm.stream("바다에 대한 짧은 시를 써줘."):
    print(chunk.content, end="", flush=True)

print()
