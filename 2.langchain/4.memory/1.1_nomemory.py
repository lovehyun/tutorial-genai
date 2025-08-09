from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate, ChatMessagePromptTemplate, HumanMessagePromptTemplate

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# | 코드 형태                                                                     실제 객체                                                       | 설명                                                                               |
# | --------------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------- |
# | `("human", "{input}")`                                                      | 내부적으로 자동 변환됨 → `HumanMessagePromptTemplate.from_template(...)` | 가장 간단한 문법. 빠르고 편함.                                              |
# | `ChatMessagePromptTemplate.from_template(role="human", template="{input}")` | `ChatMessagePromptTemplate`                                    | 역할이 `"human"`이지만, 확장 가능. 자유롭게 `role="tool"`, `"function"` 등 사용 가능 |
# | `HumanMessagePromptTemplate.from_template("{input}")`                       | `HumanMessagePromptTemplate`                                   | `role="human"` 전용으로 명확한 역할 표현. 구조가 가장 분명함.                        |


# 프롬프트 템플릿 생성
prompt1 = ChatPromptTemplate.from_messages([
    ("human", "{input}")
    # 내부적으로 HumanMessagePromptTemplate로 변환
])

prompt2 = ChatPromptTemplate.from_messages([
    ChatMessagePromptTemplate.from_template(role="human", template="{input}")
])
# 참고: LangChain에서 "human"과 "user"는 같은 역할로 간주되며, "ai"와 "assistant"도 동일하게 취급됩니다.

prompt3 = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{input}")
])
# HumanMessagePromptTemplate을 직접 사용하는 예제는 프롬프트를 더 명확하게 구성하고 싶거나, 역할을 직접 컨트롤하고 싶은 상황에서 유용합니다.

prompt4 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "당신은 친근하고 유쾌한 스포츠 전문가입니다. "
        "반말은 절대 사용하지 않고 존댓말만 씁니다. "
        "대답은 3문장 이내로 짧고 명확하게 하세요."
    ),
    HumanMessagePromptTemplate.from_template("{input}")
])

# 대화 체인 생성 - 메모리가 연결되지 않음
chain = prompt4 | llm

# 대화 수행
def chat(message):
    print(f"Q: {message}")
    response = chain.invoke({"input": message})
    print(f"A: {response.content}")

# 테스트
# chat("Hello")
# chat("Can we talk about sports?")
# chat("What's a good sport to play outdoor?")

chat("안녕하세요")
chat("운동에 대해서 이야기해 볼까요?")
chat("아웃도어 스포츠에 대해서 알려주세요.")
