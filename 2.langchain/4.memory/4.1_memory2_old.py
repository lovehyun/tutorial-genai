from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# .env 파일에서 OpenAI 키 로드
load_dotenv()

# LLM 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 메모리 초기화
memory = ConversationBufferMemory()

# 대화 체인 구성
chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 간단한 대화 테스트
chain.invoke({"input": "안녕하세요, 제 이름은 김철수입니다."})
chain.invoke({"input": "제 이름이 뭐였지요?"})
chain.invoke({"input": "저는 프로그래밍을 배우고 싶어요."})
chain.invoke({"input": "제가 무엇을 배우고 싶다고 했나요?"})
