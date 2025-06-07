import os
import time
import logging
from flask import Flask, request, send_from_directory, jsonify
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory, FileChatMessageHistory

# 환경 변수 로드
# load_dotenv('../../.env')
load_dotenv()

app = Flask(__name__, static_folder='public')
port = int(os.environ.get("PORT", 5000))

# 로깅 최소화
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# 모델 구성
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

# 프롬프트 구성
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 도움이 되는 AI 어시스턴트입니다."),
    MessagesPlaceholder(variable_name="chat_history"),  # 메모리와 연결되는 부분
    HumanMessagePromptTemplate.from_template("{input}")
])

# 체인 구성: prompt | llm | parser
chain = prompt | llm | StrOutputParser()

# 세션 ID별 히스토리를 저장하는 딕셔너리
"""
session_histories = {}

def get_memory(session_id):
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

# RunnableWithMessageHistory로 감싸기 (메모리 추가)
chat_with_memory = RunnableWithMessageHistory(
    chain,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history"
)
"""

# RunnableWithMessageHistory로 감싸기 (대화 히스토리를 파일에 저장)
os.makedirs("history", exist_ok=True)
chat_with_memory = RunnableWithMessageHistory(
    chain,
    lambda session_id: FileChatMessageHistory(f"history/{session_id}.json"),
    input_messages_key="input",
    history_messages_key="chat_history"
)

@app.route('/api/chat', methods=['POST'])
def chat():
    start = time.time() * 1000
    user_input = request.json.get('userInput', '')
    session_id = request.remote_addr  # IP 기반 세션 ID (실제 서비스는 로그인 기반 추천)

    print(f' => [사용자 요청]: {user_input}')

    try:
        response = chat_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        print("❌ 오류 발생:", e)
        response = "챗봇 응답 중 오류가 발생했습니다."

    end = time.time() * 1000
    print(f' <= [ChatGPT 응답]: {response}')
    print(f'    (처리 시간: {end - start:.2f} ms)')

    return jsonify({"chatGPTResponse": response})


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
