from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain_core.output_parsers import StrOutputParser
import tiktoken

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
token_encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

# 사용자별 대화 저장소
user_histories = {}

# 히스토리 길이 초과 시 요약하는 유틸리티
def summarize_if_needed(session_id, history):
    all_text = " ".join([msg.content for msg in history.messages])
    num_tokens = len(token_encoder.encode(all_text))

    if num_tokens > 1000:
        # 간단한 요약 요청
        summary_prompt = f"다음 대화를 요약해줘:\n\n{all_text}"
        summary = llm.invoke([HumanMessage(content=summary_prompt)]).content

        # 이전 대화 내용을 모두 삭제하고 요약으로 대체
        history.messages.clear()
        history.add_user_message("이전 대화 요약:")
        history.add_ai_message(summary)

# 프롬프트 구성
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 요약 AI야."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | llm | StrOutputParser()

# RunnableWithMessageHistory 적용
chat_chain = RunnableWithMessageHistory(
    chain,
    lambda session_id: user_histories.setdefault(session_id, InMemoryChatMessageHistory()),
    input_messages_key="input",
    history_messages_key="history"
)

# 실행 함수
def chat(message, session_id="default-user"):
    history = user_histories.setdefault(session_id, InMemoryChatMessageHistory())
    summarize_if_needed(session_id, history)

    return chat_chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )

# 테스트
print(chat("안녕, 나는 김철수야."))
print(chat("내가 누구라고 했는지 기억해?"))
print(chat("내 취미는 등산과 독서야."))
print(chat("마지막에 말한 두 가지 취미가 뭐였지?"))
print(chat("강아지도 키워. 이름은 뽀삐야."))
print(chat("내 직업은 개발자야."))
print(chat("지금까지 말한 걸 요약해줄래?"))
