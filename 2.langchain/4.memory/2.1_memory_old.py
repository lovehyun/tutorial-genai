from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 채팅 모델 설정 - 모델명 확인
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 2. 메모리 설정
memory = ConversationBufferMemory()

# 3. ConversationChain 생성 - v0.2.7부터 사용 중단(deprecated)
# ConversationChain(+ ConversationBufferMemory) -> RunnableWithMessageHistory로 교체.
chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 4. 대화 수행
def chat(message):
    print(f"Q: {message}")
    
    # conversation.predict 사용
    # response = chain.predict(input=message)  # legacy 스타일
    # print(f"A: {response}")
    
    response = chain.invoke({"input": message})  # new LCEL 표준 방식
    print(f"\n---\nHistory: \n{response['history']}\n---\n")
    print(f"A: {response['response']}")


# 테스트
# chat("Hello")
# chat("Can we talk about sports?")
# chat("What's a good sport to play outdoor?")

# chat("안녕하세요")
# chat("운동에 대해서 이야기해 볼까요?")
# chat("아웃도어 스포츠에 대해서 알려주세요.")

chat("안녕하세요, 제 이름은 김철수입니다.")
chat("제 이름이 뭐였지요?")
chat("저는 프로그래밍을 배우고 싶어요.")
chat("제가 무엇을 배우고 싶다고 했나요?")
