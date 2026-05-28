"""
ChatOllama — OpenAI 대신 로컬에서 돌아가는 LLM.
이 예제: Ollama 서버에 띄운 모델로 가장 단순한 채팅 (RAG 빼고 LLM 만).

준비 (한 번만):
  1. Ollama 설치: https://ollama.com/download
  2. 모델 받기 (예: 가벼운 llama3.2:3b):
       ollama pull llama3.2:3b
  3. Ollama 서버 자동 실행 중인지 확인 (백그라운드 데몬)
  4. pip install langchain-ollama

OpenAI 와 비교:
  - 비용 0, 데이터 외부 유출 X, 오프라인 동작
  - 대신 모델 다운로드 용량 + 로컬 GPU/CPU 자원 필요
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# OpenAI 의 ChatOpenAI 와 인터페이스 거의 동일 — model 이름만 다름
llm = ChatOllama(model="llama3.2:3b", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다. 간결히 답하세요."),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()

print(chain.invoke({"question": "RAG 가 뭔지 한 문단으로 설명해줘."}))

# 다음 (2_rag.py): 같은 인터페이스라 RAG 체인의 LLM 만 ChatOllama 로 갈아끼우면 끝.
