"""
LLM 캐시 — 동일 입력 재호출 시 비용/지연을 0 으로

운영 환경에서 같은 요청이 반복되는 경우 응답을 캐싱해 LLM 호출 자체를 건너뜁니다.
  - InMemoryCache : 프로세스 내 메모리 (테스트/단일 서버용)
  - SQLiteCache   : 파일 기반 영구 캐시 (간단한 운영)
  - 그 외 Redis 등도 지원
"""

import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

load_dotenv()

# 전역 LLM 캐시 활성화
set_llm_cache(InMemoryCache())

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)   # 캐시 효과 보려면 temperature=0
chain = ChatPromptTemplate.from_template("{q}") | llm | StrOutputParser()

q = {"q": "파이썬에서 리스트와 튜플의 차이를 한 줄로."}

# 1회차: 실제 호출 → 느림
t0 = time.time()
print(chain.invoke(q))
print(f"[1회차]  {time.time()-t0:.2f}s (실제 API 호출)")

# 2회차: 캐시 hit → 즉시 반환
t0 = time.time()
print(chain.invoke(q))
print(f"[2회차]  {time.time()-t0:.2f}s (캐시 적중 — 비용 0)")
