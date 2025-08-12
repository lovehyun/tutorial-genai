# pip install anthropic
#
# 항목                     변경 전 (openai)                     변경 후 (anthropic)
# API Key 환경변수 이름     OPENAI_API_KEY	                    ANTHROPIC_API_KEY
# 클라이언트 생성 방식	    openai = OpenAI(...)	             anthropic = Anthropic(...)
# 메시지 요청 메서드        openai.chat.completions.create(...)	 anthropic.messages.create(...)
# 응답 포맷	               response.choices[0].message.content	 response.content[0].text

import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from anthropic import Anthropic

# 환경변수 로드 (.env)
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# Anthropic 클라이언트 초기화
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route("/")
def index():
    # public 폴더 안의 index.html을 반환
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/check", methods=["POST"])
def check_code():
    data = request.get_json()
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "소스코드가 입력되지 않았습니다."}), 400

    prompt = (
        "다음 소스코드에서 보안 취약점을 분석해줘.\n"
        "각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 개선 방안을 간단하게 설명해줘. 주석은 무시해도 돼.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        f"{code}\n"
        "------------------------------"
    )

    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",  # 또는 claude-3-opus
            max_tokens=1024,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        analysis = response.content[0].text  # Claude는 content가 list로 옴
    except Exception as e:
        analysis = f"분석 중 에러 발생: {str(e)}"

    return jsonify({"analysis": analysis})

if __name__ == "__main__":
    app.run(debug=True)
