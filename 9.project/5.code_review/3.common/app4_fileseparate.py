import os
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# 분석 모듈 임포트 (lc 버전을 쓸 경우 설치 필요)
# pip install langchain langchain-openai langchain-anthropic
# pip install openai anthropic
from analyzers import openai_analyzer, anthropic_analyzer

load_dotenv()
app = Flask(__name__, static_folder='public', static_url_path='')

def convert_github_url_to_raw(url):
    # 정규표현식으로 처리
    pattern = r"https://github.com/(.+)/blob/(.+)"
    match = re.match(pattern, url)
    if match:
        return f"https://raw.githubusercontent.com/{match.group(1)}/{match.group(2)}"
    return url

def add_line_numbers(code):
    lines = code.splitlines()
    return "\n".join([f"{i+1:4d}: {line}" for i, line in enumerate(lines)])

@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index3.html')

@app.route("/api/check", methods=["POST"])
def check_code():
    data = request.get_json()
    github_url = data.get("github_url")
    provider = data.get("provider", "openai")

    if not github_url:
        return jsonify({"error": "github_url 필드가 필요합니다."}), 400

    # 1. 주소 변환
    raw_url = convert_github_url_to_raw(github_url)

    # 2. 요청
    try:
        resp = requests.get(raw_url)
        resp.raise_for_status()
        code = resp.text
    except Exception as e:
        return jsonify({"error": f"파일을 가져오는 중 에러 발생: {e}"}), 500

    # 3. 소스코드에 줄번호 추가
    numbered_code = add_line_numbers(code)
    print(numbered_code)

    # 4. 분석
    print("모델 요청: ", provider)
    try:
        if provider == "openai":
            analysis = openai_analyzer.analyze(numbered_code)
        elif provider == "anthropic":
            analysis = anthropic_analyzer.analyze(numbered_code)
        else:
            analysis = "아직 구현되지 않은 모델입니다."
            
    except Exception as e:
        return jsonify({"error": f"{provider.upper()} 분석 중 에러 발생: {e}"}), 500

    return jsonify({
        "code": code,
        "analysis": analysis
    })

if __name__ == "__main__":
    app.run(debug=True)
