"""
RunnableMap — RunnableParallel 의 별칭(완전 동일 클래스).
이 예제: RunnableMap is RunnableParallel 이 True 임을 확인하고 동일 동작을 비교합니다.

import 만 다르고 동일한 객체입니다.
  - RunnableParallel: "여러 체인을 병렬 실행"이라는 의도를 강조할 때
  - RunnableMap:      "여러 키를 동시에 만든다"는 의도를 강조할 때
실제로는 어떤 이름을 써도 동작이 같습니다.
"""

from langchain_core.runnables import RunnableMap, RunnableParallel

# 1) 같은 클래스인지 직접 확인
print("RunnableMap is RunnableParallel?", RunnableMap is RunnableParallel)
# True 가 출력됩니다.


# 2) 같은 동작 — 둘 다 같은 결과
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
chain = ChatPromptTemplate.from_template("{x}를 한국어로 번역") | llm | StrOutputParser()

via_map      = RunnableMap({"a": chain, "b": chain})
via_parallel = RunnableParallel({"a": chain, "b": chain})

print("\n[RunnableMap 결과]")
print(via_map.invoke({"x": "hello"}))

print("\n[RunnableParallel 결과]")
print(via_parallel.invoke({"x": "hello"}))

# 결론: 이름 선택은 가독성·의도 표현용. 새 코드는 RunnableParallel 권장.
