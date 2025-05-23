import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# .env 파일의 환경변수 로드
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# LLM 초기화 (OpenAI)
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=2048  # 응답 토큰 최대 길이 설정
)

# LangChain 체인 구성
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 보안 코드 분석 전문가입니다."),
    ("user", """다음 소스코드에서 보안 취약점을 분석해줘.
각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 개선 방안을 간단하게 설명해줘. 주석은 무시해도 돼.

소스코드:
------------------------------
{code}
------------------------------""")
])

chain = prompt | llm | StrOutputParser()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/check", methods=["POST"])
def check_code():
    data = request.get_json()
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "소스코드가 입력되지 않았습니다."}), 400

    try:
        analysis = chain.invoke({"code": code})
    except Exception as e:
        analysis = f"분석 중 에러 발생: {str(e)}"
    
    return jsonify({"analysis": analysis})

if __name__ == "__main__":
    app.run(debug=True)
