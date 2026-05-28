"""
RunnableLambda — 임의의 파이썬 함수를 체인 단계로 끼우는 Runnable.
이 예제: 값은 그대로 흘리되 콘솔에 print 만 하는 RunnableLambda 로 중간 값을 디버깅합니다.

체인 중간에 print 하는 RunnableLambda 를 끼워서 흐르는 값을 들여다봅니다.
값은 그대로 다음 단계로 흘려보냅니다(부수효과만 발생).
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

name_prompt = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사 이름을 1개만 추천해줘. 이름만 답해."
)
name_chain = name_prompt | llm | StrOutputParser()

slogan_prompt = ChatPromptTemplate.from_template(
    "'{company_name}' 회사의 슬로건을 한 줄로 만들어줘."
)
slogan_chain = slogan_prompt | llm | StrOutputParser()


def debug(label):
    """값은 그대로 흘려보내고, 콘솔에만 찍는다."""
    def _peek(x):
        print(f"[{label}] {x}")
        return x
    return RunnableLambda(_peek)


pipeline = (
    name_chain
    | debug("회사명 생성 직후")                          # 중간 관찰 1
    | RunnableLambda(lambda name: {"company_name": name.strip()})
    | debug("dict 변환 직후")                            # 중간 관찰 2
    | slogan_chain
    | debug("최종 슬로건")                                # 중간 관찰 3
)

result = pipeline.invoke({"product": "웹게임"})
print("\n최종 결과:", result)
