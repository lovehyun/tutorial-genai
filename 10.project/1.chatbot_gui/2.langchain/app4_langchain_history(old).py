import os
import time
import logging
from flask import Flask, request, send_from_directory, jsonify
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# 환경 변수 로드
# load_dotenv('../../.env')
load_dotenv()

app = Flask(__name__, static_folder='public')
port = int(os.environ.get("PORT", 5000))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 불필요한 로그 끄기
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# OpenAI LLM 구성
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

# 메모리 구성
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 커스텀 프롬프트 구성
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 도움이 되는 AI 어시스턴트입니다."),
    MessagesPlaceholder(variable_name="chat_history"),  # 메모리와 연결되는 부분
    HumanMessagePromptTemplate.from_template("{input}")
])

# 체인 구성
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

@app.route('/api/chat', methods=['POST'])
def chat():
    start = time.time() * 1000
    user_input = request.json.get('userInput', '')
    print(f' => [사용자 요청]: {user_input}')

    try:
        response = chain.run(input=user_input)
    except Exception as error:
        print('❌ ChatGPT 처리 중 오류:', error)
        response = '챗봇 응답을 가져오는 도중 오류가 발생했습니다.'

    end = time.time() * 1000
    print(f' <= [ChatGPT 응답]: {response}')
    print(f'    (요청 및 응답 시간: {end - start:.2f} ms)')

    return jsonify({"chatGPTResponse": response})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
