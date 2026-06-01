"""
Flask RAG 웹앱 #1 — 최소 MVP.
이 예제: PDF 업로드 + 질문 응답을 한 파일에 다 담은 가장 단순한 버전.

핵심 흐름:
  POST /upload  → PDF 파일 받아 청크 → 벡터 DB에 추가
  POST /ask     → 질문 받아 검색 → LLM 답변
  GET  /        → 단일 페이지 HTML

다음 단계 (#2): 점수/출처 표시 + 로딩 UI + services/ 모듈 분리
"""

import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

DATA_DIR        = "../DATA"         # 1~5 공유 (= 8.web_app/DATA)
PERSIST_DIR     = "../chroma_db"    # 벡터 DB 도 8.web_app 안에서 공유
COLLECTION_NAME = "rag_web"

os.makedirs(DATA_DIR, exist_ok=True)

# ─── 벡터 스토어 (전역) ────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

# ─── RAG 체인 ──────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])
chain = prompt | llm | StrOutputParser()


def add_pdf(file_path: str):
    """PDF 를 청킹해서 벡터 DB 에 추가"""
    docs   = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = os.path.basename(file_path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)


def answer_question(question: str) -> str:
    if store._collection.count() == 0:
        return "먼저 PDF를 업로드해주세요."
    docs = store.similarity_search(question, k=5)
    context = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"context": context, "question": question})


# ─── Flask ─────────────────────────────────────────────
app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "파일이 없습니다"}), 400
    path = os.path.join(DATA_DIR, file.filename)
    file.save(path)
    add_pdf(path)
    return jsonify({"message": f"'{file.filename}' 업로드 완료"})


@app.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify({"answer": answer_question(question)})


if __name__ == "__main__":
    # app.run(debug=True, use_reloader=False, port=5001)
    app.run(debug=True, port=5001)


# 기능	            use_reloader=True	use_reloader=False
# 디버그 페이지	            O	            O
# 예외 스택트레이스	        O           	O
# 코드 수정 시 자동 재시작	O	            X
# 시작 시 두 번 실행	    O	            X
# 무거운 초기화 두 번 수행	O	            X


# 프로세스 #1
# ↓
# 소스 파일 감시자(Watcher) 시작
# ↓
# 프로세스 #2 재실행
# ↓
# 실제 서버 동작
