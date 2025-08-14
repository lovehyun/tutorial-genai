# LLM 5일차: RAG를 통한 웹 서비스 (업로드 + 질의 응답)

## 학습 목표
- **문서 업로드 → 인덱싱 → 질의**를 웹 API로 제공합니다.
- Flask 백엔드 + Chroma 영속 저장, CORS/스트리밍을 포함한 실전형 샘플을 완성합니다.

---

## 설치
```bash
pip install flask flask-cors python-dotenv langchain langchain-openai chromadb pypdf tiktoken
```

## 구조
```
rag_service/
 ├─ app.py
 ├─ rag.py          # 체인/인덱싱 유틸
 ├─ .env
 └─ uploads/        # 업로드 파일
```

### .env
```
OPENAI_API_KEY=sk-...
```

---

## rag.py
```python
# rag.py
import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_DIR = "chroma_db"
COLLECTION = "service-docs"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

emb = OpenAIEmbeddings(model="text-embedding-3-small")

def open_vs():
    return Chroma(collection_name=COLLECTION, persist_directory=DB_DIR, embedding_function=emb)

def load_and_split(path: Path):
    if path.suffix.lower() == ".pdf":
        docs = PyPDFLoader(str(path)).load()
    else:
        docs = TextLoader(str(path), encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    return splitter.split_documents(docs)

def ingest(path: Path):
    vs = open_vs()
    chunks = load_and_split(path)
    vs.add_documents(chunks); vs.persist()
    return len(chunks)

SYSTEM = (
"당신은 업로드 문서를 근거로 답하는 비서입니다. "
"근거가 없으면 '정보가 부족합니다.'라고 답하세요."
)

def build_chain():
    vs = open_vs()
    retriever = vs.as_retriever(search_kwargs={"k":4})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        ("human", "질문: {question}\n컨텍스트: {context}")
    ])
    def fmt(docs):
        return "\n\n".join(d.page_content for d in docs)
    chain = ({"context": retriever | fmt, "question": lambda x: x["q"]}
             | prompt | llm | StrOutputParser())
    return chain
```

---

## app.py
```python
# app.py
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
from rag import ingest, build_chain, UPLOAD_DIR

load_dotenv()
app = Flask(__name__)
CORS(app)

chain = build_chain()

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return {"error":"file is required"}, 400
    f = request.files["file"]
    path = UPLOAD_DIR / f.filename
    f.save(path)
    n = ingest(path)
    return {"ok": True, "chunks_indexed": n}

@app.post("/ask")
def ask():
    data = request.get_json(force=True)
    q = data.get("question","").strip()
    if not q: return {"error":"question is required"}, 400
    ans = chain.invoke({"q": q})
    return {"answer": ans}

@app.post("/ask/stream")
def ask_stream():
    data = request.get_json(force=True)
    q = data.get("question","")
    def generate():
        try:
            for chunk in chain.astream({"q": q}):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

---

## 간단 테스트 HTML (업로드/질의)
```html
<!doctype html>
<html>
  <body>
    <h3>업로드</h3>
    <input type="file" id="f">
    <button onclick="up()">Upload</button>
    <pre id="u"></pre>

    <h3>질의</h3>
    <input id="q" placeholder="질문">
    <button onclick="ask()">Ask</button>
    <pre id="a"></pre>

    <script>
      async function up(){
        const fd = new FormData();
        fd.append('file', document.getElementById('f').files[0]);
        const r = await fetch('http://localhost:8000/upload', {method:'POST', body:fd});
        document.getElementById('u').textContent = await r.text();
      }
      async function ask(){
        const q = document.getElementById('q').value;
        const r = await fetch('http://localhost:8000/ask', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({question:q})
        });
        document.getElementById('a').textContent = await r.text();
      }
    </script>
  </body>
</html>
```

---

## 운영 팁
- 업로드 확장자 화이트리스트, 파일 크기 제한
- 비동기 인덱싱(큐)로 응답 성능 확보
- 문서 메타데이터(부서/권한) 기반 필터링
- 로그/모니터링, 예외 핸들링 표준화
