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
    # model="gpt-3.5-turbo",
    model="gpt-4o",
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
    start_ms = time.time() * 1000
    user_input = request.json.get('userInput', '')
    print(f' => [사용자 요청]: {user_input}')
    logger.info("⇒ 사용자 요청: %s", user_input)

    try:
        chatgpt_response = chain.invoke({"user_input": user_input})
    except Exception as error:
        print('[ERROR] ChatGPT 처리 중 오류:', error)
        logger.exception("ChatGPT 처리 중 예외 발생")  # 파이썬이 자동으로 현재 예외 객체 (sys.exc_info())를 감지해서 로그에 같이 출력함 (Stacktrace 포함됨)
                                                      # logger.error("에러 발생: %s", e)를 쓰면 예외 정보는 수동으로 추가해야 함
        chatgpt_response = '챗봇 응답을 가져오는 도중 오류가 발생했습니다.'

    end_ms = time.time() * 1000
    elapsed = end_ms - start_ms
    print(f' <= [ChatGPT 응답]: {chatgpt_response}')
    print(f'    (요청 및 응답 시간: {elapsed:.2f} ms)')
    logger.info("⇐ ChatGPT 응답 (%.2f ms)", elapsed)

    return jsonify({'chatGPTResponse': chatgpt_response})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    logger.info("Flask 서버 시작: http://0.0.0.0:%d", port)
    app.run(host='0.0.0.0', port=port)
