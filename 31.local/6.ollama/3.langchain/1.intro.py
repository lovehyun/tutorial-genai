# pip install langchain-ollama
#
# Ollama + LangChain 1: 가장 단순한 호출.
# raw `ollama` 라이브러리 대신 LangChain 의 ChatOllama 로 감싼다.
# 먼저: ollama serve (기본 localhost:11434) + ollama pull qwen2.5:1.5b

from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:1.5b", temperature=0.7)   # 교체(저사양): qwen2.5:0.5b(~0.4G)·llama3.2:1b(~1.3G)·gemma2:2b(~1.6G)·mistral(7b,~4G) — README

# 문자열을 주면 AIMessage 가 돌아온다. 본문은 .content
resp = llm.invoke("안녕? 한 문장으로 자기소개 해줘.")
print(resp.content)
