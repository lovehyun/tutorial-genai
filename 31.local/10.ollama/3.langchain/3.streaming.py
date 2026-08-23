# pip install langchain-ollama
#
# Ollama + LangChain 3: 스트리밍.
# .stream() 은 토큰 조각(AIMessageChunk)을 순서대로 내준다.

from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:1.5b")   # 교체(저사양): qwen2.5:0.5b(~0.4G)·llama3.2:1b(~1.3G)·gemma2:2b(~1.6G)·mistral(7b,~4G) — README

for chunk in llm.stream("바다에 대한 짧은 시를 써줘."):
    print(chunk.content, end="", flush=True)

print()
