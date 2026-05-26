# OpenAI 스트리밍 - 1단계: 템플릿 엔진 방식 (Flask render_template)
# pip install flask openai python-dotenv
#
# 같은 스트리밍 채팅을 '웹앱 구조'를 달리해 두 가지로 만든다 — 이 파일은 템플릿 엔진 방식.
#   - 서버가 HTML을 Jinja 템플릿 엔진으로 처리해서 내려준다 (서버 사이드 렌더링).
#   - 서버의 데이터를 {{ 변수 }}로 HTML에 끼워넣을 수 있다 (아래 title 참고).
#   - HTML은 templates/ 폴더에 둔다. 프론트와 백이 한 몸처럼 묶인다.
# 프론트/백을 분리하는 REST API 방식은 2단계.
#
# 참고: OpenAI 호출은 두 파일 모두 SDK(stream=True)를 쓴다 — 거기엔 차이가 없다.

import os
import json

from dotenv import load_dotenv
from flask import Flask, render_template, request, Response
from openai import OpenAI

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

# [관전 포인트] render_template — templates/index.html을 템플릿 엔진으로 처리한다.
#   title 값이 HTML의 {{ title }} 자리에 서버에서 채워져 내려간다.
@app.route('/')
def index():
    return render_template('index.html', title='OpenAI SSE 스트리밍 — 템플릿 엔진 방식')

# SSE 스트리밍 엔드포인트 (2단계와 완전히 동일한 코드)
@app.route('/stream', methods=['POST'])
def stream():
    user_message = request.json.get('message', '')

    def generate():
        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다. 한국어로 답변하세요.'},
                    {'role': 'user', 'content': user_message},
                ],
                stream=True,
                temperature=0.7,
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print('OpenAI SSE 스트리밍 서버 (템플릿 엔진 방식)')
    print('브라우저에서 http://localhost:5000 접속')
    app.run(debug=True)
