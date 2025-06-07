import os
import time
import logging

from flask import Flask, request, send_from_directory, jsonify
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 환경 변수 로드
# load_dotenv('../../.env')
load_dotenv()

app = Flask(__name__, static_folder='public')
port = int(os.environ.get("PORT", 5000))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI LLM 구성
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

# 프롬프트 템플릿 구성 (LangChain 스타일)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 도움이 되는 AI 어시스턴트입니다."),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

# 체인 구성: 프롬프트 → LLM → 문자열 파서
chain = prompt | llm | StrOutputParser()

@app.route('/api/chat', methods=['POST'])
def chat():
    start = time.time() * 1000
    user_input = request.json.get('userInput', '')
    print(f' => [사용자 요청]: {user_input}')

    try:
        chatgpt_response = chain.invoke({"user_input": user_input})
    except Exception as error:
        print('❌ ChatGPT 처리 중 오류:', error)
        chatgpt_response = '챗봇 응답을 가져오는 도중 오류가 발생했습니다.'

    end = time.time() * 1000
    print(f' <= [ChatGPT 응답]: {chatgpt_response}')
    print(f'    (요청 및 응답 시간: {end - start:.2f} ms)')

    return jsonify({'chatGPTResponse': chatgpt_response})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
