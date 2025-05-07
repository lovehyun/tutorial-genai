from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# .env 파일에서 환경 변수 로드
load_dotenv()

# LLM 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.7)

# 메모리 초기화
memory = ConversationBufferMemory()

# 대화 체인 생성
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 첫 번째 입력
response1 = conversation.invoke({"input": "안녕하세요, 제 이름은 김철수입니다."})
print(response1["response"])

# 두 번째 입력 (이전 대화 기억)
response2 = conversation.invoke({"input": "제 이름이 뭐였지요?"})
print(response2["response"])

# 세 번째 입력
response3 = conversation.invoke({"input": "저는 프로그래밍을 배우고 싶어요."})
print(response3["response"])

# 네 번째 입력 (이전 대화 기억)
response4 = conversation.invoke({"input": "제가 무엇을 배우고 싶다고 했나요?"})
print(response4["response"])
