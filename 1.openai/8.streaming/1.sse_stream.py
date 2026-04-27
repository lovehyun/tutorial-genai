# pip install openai flask

import openai
from dotenv import load_dotenv
import os
from flask import Flask, Response, request, render_template
import json

load_dotenv(dotenv_path='../../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api_key)

app = Flask(__name__)

# 1. 메인 페이지 (templates/index.html 렌더링)
@app.route('/')
def index():
    return render_template('index.html')

# 2. SSE 스트리밍 엔드포인트
@app.route('/stream', methods=['POST'])
def stream():
    data = request.json
    user_message = data.get('message', '')

    def generate():
        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다. 한국어로 답변하세요.'},
                    {'role': 'user', 'content': user_message}
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1000,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# 3. 실행
if __name__ == '__main__':
    print("=" * 50)
    print("OpenAI SSE 스트리밍 서버")
    print("=" * 50)
    print("브라우저에서 http://localhost:5000 접속")
    print("-" * 50)
    app.run(debug=True)
