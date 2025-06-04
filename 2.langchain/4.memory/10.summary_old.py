from dotenv import load_dotenv
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

load_dotenv()

# 요약용 LLM 정의 (보통 gpt-3.5 사용)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 메모리 정의
memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True
)

# 체인 구성
chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 대화 예시
print(chain.invoke("안녕, 나는 홍길동 이라고 해"))
print(chain.invoke("내가 누구라고 했는지 기억해?"))
print(chain.invoke("내가 좋아하는 취미는 독서야."))
print(chain.invoke("내가 어떤 취미를 좋아한다고 했지?"))
