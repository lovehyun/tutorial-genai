# OpenAI 스트리밍 - 단순화 버전 (템플릿 엔진 방식)
# pip install flask openai python-dotenv
#
# 1.chat 폴더의 SSE 버전과 동작은 같지만 — 포장지를 다 벗긴 형태다.
#   - 1.chat 서버:  yield f"data: {json.dumps({'content': ...})}\n\n"  ← SSE 포맷으로 감싸기
#   - 여기 서버:    yield content                                       ← 토큰 텍스트 그대로
#   - 1.chat 클라: split('\n') → startsWith('data: ') → slice(6) → JSON.parse (4단계)
#   - 여기 클라:   받은 청크를 그대로 화면에 붙이면 끝
#
# 'fetch + ReadableStream'으로도 충분히 스트리밍이 된다. SSE 포맷(data:/event:/id:)은
# 여러 이벤트 타입을 구분하거나 EventSource API를 쓸 때나 의미가 있다 — 단일 텍스트 흐름만
# 받을 거면 굳이 만들 필요가 없다.

import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, Response
from openai import OpenAI

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='OpenAI 스트리밍 — 단순화 (템플릿 엔진)')

@app.route('/stream', methods=['POST'])
def stream():
    user_message = request.json.get('message', '')

    def generate():
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다. 한국어로 답변하세요.'},
                {'role': 'user', 'content': user_message},
            ],
            stream=True,
            temperature=0.7,
        )
        # [관전 포인트] SSE 포장(data:, \n\n, [DONE])을 안 한다.
        #   OpenAI가 주는 토큰을 그대로 yield → Flask가 HTTP chunked transfer로 흘려보낸다.
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    # mimetype도 'text/event-stream'이 아니라 그냥 'text/plain'으로 충분하다.
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    print('OpenAI 스트리밍 서버 — 단순화 (템플릿 엔진 방식)')
    print('브라우저에서 http://localhost:5000 접속')
    app.run(debug=True)
