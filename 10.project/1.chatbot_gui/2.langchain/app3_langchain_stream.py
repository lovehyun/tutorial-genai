import os
import logging
from time import time

from flask import Flask, request, send_from_directory, Response, stream_with_context
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# LangChain은 기본적으로 비동기 스트리밍 지원이 제한적입니다.
# 하지만 LangChain에서도 GPT 응답을 stream=True로 받아서 실시간으로 generator(yield) 형식으로 처리할 수는 있습니다. 
# 이를 Flask 스트리밍 방식과 접목하려면 LangChain 체인을 구성하면서 LLM을 스트리밍 가능한 형태로 만들고, chain.stream()을 사용하는 방식으로 구성해야 합니다.

# 환경 변수 로드
# load_dotenv('../../.env')
load_dotenv()

app = Flask(__name__, static_folder='public')
port = int(os.environ.get("PORT", 5000))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 스트리밍 가능한 LLM 구성
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY"),
    streaming=True  # 핵심: 스트리밍 활성화
)

# LangChain 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 도움이 되는 AI 어시스턴트입니다."),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

# 체인 구성
chain = prompt | llm

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get("userInput", "")
    print(f"[사용자 요청]: {user_input}")

    def generate():
        try:
            for chunk in chain.stream({"user_input": user_input}):
                # 각 chunk는 langchain_core.messages.AIMessageChunk
                yield chunk.content
        except Exception as e:
            yield f"[오류 발생] {str(e)}"

    return Response(stream_with_context(generate()), content_type="text/plain")


@app.route('/')
def index():
    return send_from_directory("public", "index2_stream.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
