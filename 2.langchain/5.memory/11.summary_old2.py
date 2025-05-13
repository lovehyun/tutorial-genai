from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

# 1. 환경 변수 로드
load_dotenv()

# 2. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. 요약 메모리 생성
memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="history",
    return_messages=True,
    max_token_limit=1000  # 토큰 초과 시 요약 발생
)

# 4. 대화 체인 구성 (RunnableWithMessageHistory는 지원 안 됨)
chain = ConversationChain(llm=llm, memory=memory, verbose=True)

# 5. 대화 진행
conversation = [
    "안녕, 나는 김철수라고 해.",
    "내가 누구라고 했는지 기억해?",
    "내 취미는 등산과 독서야.",
    "그 취미 기억하고 있어?",
    "내가 마지막에 말한 두 가지 취미는 뭐였지?",
    "강아지를 키우고 있어. 이름은 뽀삐야.",
    "내 직업은 개발자야.",
    "지금까지 말한 걸 요약해줄래?"
]

for message in conversation:
    response = chain.invoke(message)
    print(f"Human: {message}")
    print(f"AI: {response}\n")

# 6. 요약 결과 저장
print("현재 요약:", repr(memory.moving_summary_buffer))
# if memory.moving_summary_buffer.strip():
#     with open("final_summary.txt", "w", encoding="utf-8") as f:
#         f.write(memory.moving_summary_buffer)
#     print("요약이 저장되었습니다.")
# else:
#     print("요약이 아직 생성되지 않았습니다.")
