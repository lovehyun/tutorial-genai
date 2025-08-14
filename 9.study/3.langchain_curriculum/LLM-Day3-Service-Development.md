# LLM 3일차: LLM을 사용한 서비스 개발 (Flask 기반)

## 학습 목표
- Flask로 **실전 챗 API**를 설계/구현합니다.
- CORS, 로깅, 예외 처리, 스트리밍(SSE)까지 포함한 **프로덕션 초안**을 완성합니다.
- LangChain 체인을 백엔드 엔드포인트로 노출합니다.

---

## 설치
```bash
pip install flask flask-cors python-dotenv langchain langchain-openai tiktoken
```

## 프로젝트 구조 예시
```
service/
 ├─ app.py
 ├─ chain.py
 ├─ .env
 └─ requirements.txt
```

### .env
```
OPENAI_API_KEY=sk-...
```

---

## 체인 정의 (`chain.py`)
```python
# chain.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SYSTEM = "당신은 정확하고 간결한 한국어 비서입니다."
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()
```

---

## Flask API (`app.py`)
```python
# app.py
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import json, time, traceback, os
from chain import chain

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/chat")
def chat():
    try:
        data = request.get_json(force=True)
        question = data.get("question","").strip()
        if not question:
            return jsonify({"error":"question is required"}), 400
        answer = chain.invoke({"question": question})
        return jsonify({"answer": answer})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Server-Sent Events(텍스트 스트리밍)
@app.post("/chat/stream")
def chat_stream():
    data = request.get_json(force=True)
    question = data.get("question","").strip()

    def generate():
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
            prompt = ChatPromptTemplate.from_template("한 문장으로 응답: {q}")
            s_chain = prompt | llm | StrOutputParser()

            for chunk in s_chain.astream({"q": question}):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

---

## 프론트엔드(테스트용) — 순수 HTML/JS
> 템플릿 엔진 없이 호출 확인용

```html
<!doctype html>
<html>
  <body>
    <h3>/chat 테스트</h3>
    <input id="q" placeholder="질문" />
    <button onclick="send()">Ask</button>
    <pre id="out"></pre>

    <script>
      async function send(){
        const q = document.getElementById('q').value;
        const res = await fetch('http://localhost:8000/chat', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({question:q})
        });
        document.getElementById('out').textContent = await res.text();
      }
    </script>

    <h3>/chat/stream 테스트</h3>
    <input id="q2" placeholder="질문(스트리밍)" />
    <button onclick="sendStream()">Stream</button>
    <pre id="out2"></pre>
    <script>
      async function sendStream(){
        const q = document.getElementById('q2').value;
        const res = await fetch('http://localhost:8000/chat/stream', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({question:q})
        });
        const reader = res.body.getReader();
        const dec = new TextDecoder();
        let buf = "";
        while(true){
          const {value, done} = await reader.read();
          if(done) break;
          buf += dec.decode(value, {stream:true});
          document.getElementById('out2').textContent = buf;
        }
      }
    </script>
  </body>
</html>
```

---

## 로깅 & 에러 처리 팁
- 요청 ID/사용자 ID/세션 ID 로깅
- 예외 스택을 서버 로그에 저장, 클라이언트에는 일반화된 메시지
- 타임아웃/재시도/서킷브레이커(필요 시)

---

## 실습 과제
1) `/chat`에 **system 지시**를 동적으로 받는 파라미터 추가.  
2) `/chat/stream`을 UI에서 단어 단위로 타이핑 효과 구현.  
3) 간단한 **요금/토큰** 로깅 미들웨어 추가.
