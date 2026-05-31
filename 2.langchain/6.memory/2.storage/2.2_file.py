"""
FileChatMessageHistory — JSON 파일에 대화 저장

2.1 과 비교: storage 객체 한 줄만 다릅니다.
프로세스 종료 후에도 history.json 에 대화가 남아 다음 실행에 그대로 이어집니다.
"""

# pip install langchain-community
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# 2.1 과 비교: storage 한 줄만 다름
HISTORY_FILE = "history.json"

# 매번 깨끗하게 시작하고 싶으면 아래 줄 활성화
# open(HISTORY_FILE, "w", encoding="utf-8").write(json.dumps([]))

history = FileChatMessageHistory(HISTORY_FILE)


def chat(message):
    print(f"\nQ: {message}")
    answer = chain.invoke({
        "input":   message,
        "history": history.messages,
    })
    print(f"A: {answer}")
    history.add_user_message(message)
    history.add_ai_message(answer)


chat("제 이름은 홍길동입니다.")
chat("저는 등산을 좋아해요.")
chat("제 이름과 취미를 다시 말해줄래요?")

# 실행 후 history.json 을 열어보세요. JSON 으로 메시지가 그대로 저장돼 있습니다.
# 다시 실행하면 이전 대화 그 자리에 누적되어, 모델이 처음부터 기억합니다.
