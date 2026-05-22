# OpenAI 스트리밍 - 2단계: REST API 방식 (정적 프론트엔드 + API 백엔드)
# pip install flask openai python-dotenv
#
# 1단계와 동작은 똑같고 '웹앱 구조'만 다르다 — 이 파일은 REST API 방식.
#   - 백엔드는 순수 API 서버다. HTML을 가공하지 않고 정적 파일 그대로 내려준다.
#   - 프론트엔드(public/index.html)는 독립된 정적 파일 — API를 fetch로 호출한다.
#   - 프론트와 백이 분리돼 있어 프론트를 다른 서버/CDN에 둘 수도 있다.
#   (이 repo의 다른 챗봇 예제들이 쓰는 구조와 동일하다.)
#
# 참고: OpenAI 호출은 두 파일 모두 SDK(stream=True)를 쓴다 — 거기엔 차이가 없다.

import os
import json
from flask import Flask, Response, request, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# static_folder='public' — 정적 프론트엔드 파일을 두는 폴더
app = Flask(__name__, static_folder='public')

# [관전 포인트] 템플릿 엔진을 거치지 않고 public/index.html을 '그대로' 내려준다.
#   서버는 HTML 내용에 관여하지 않는다 — 프론트엔드는 완전히 독립적이다.
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# SSE 스트리밍 엔드포인트 (1단계와 완전히 동일한 코드)
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
    print('OpenAI SSE 스트리밍 서버 (REST API 방식)')
    print('브라우저에서 http://localhost:5000 접속')
    app.run(debug=True)
