"""
Flask RAG 웹앱 #1 — 최소 MVP (지연 로딩 버전).

app.py 와 동작은 같지만, 무거운 초기화(임베딩 모델 / 벡터 스토어 / LLM)를
import 시점이 아니라 "처음 실제로 필요할 때 한 번만" 수행한다.

왜 이렇게?
  debug=True 면 Flask reloader 가 프로세스를 둘 띄운다.
    프로세스 #1 = 소스 파일 감시자(watcher)   ← 요청을 처리하지 않음
    프로세스 #2 = 실제 서버
  두 프로세스 모두 이 모듈을 import 하므로, 전역 변수에서 바로 초기화하면
  무거운 초기화가 2번 실행되어 시작이 느려진다.

  → 초기화를 함수 안으로 미루면(lazy):
      - 감시자 프로세스는 요청이 없으니 초기화를 아예 하지 않는다.
      - 실제 서버도 첫 /upload 또는 /ask 요청 때 단 한 번만 초기화한다.
    결과적으로 서버 "시작"은 즉시 끝난다.

참고: @app.before_serving 은 Flask 가 아니라 Quart(비동기) 전용 데코레이터다.
      Flask 의 @app.before_first_request 도 2.3 에서 제거되었으므로,
      Flask 에서는 아래처럼 직접 지연 초기화(싱글톤) 하는 것이 표준이다.

다음 단계 (#2): 점수/출처 표시 + 로딩 UI + services/ 모듈 분리
"""

import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

DATA_DIR        = "../DATA"         # 1~5 공유 (= 8.web_app/DATA)
PERSIST_DIR     = "../chroma_db"    # 벡터 DB 도 8.web_app 안에서 공유
COLLECTION_NAME = "rag_web"

os.makedirs(DATA_DIR, exist_ok=True)

# ─── 지연 초기화 대상 (처음엔 전부 None) ────────────────
# import 시점에는 만들지 않는다. _ensure_ready() 가 첫 호출 때 채운다.
store = None   # Chroma 벡터 스토어
llm   = None   # ChatOpenAI
chain = None   # prompt | llm | parser


def _ensure_ready():
    """무거운 초기화를 처음 한 번만 수행한다(싱글톤).

    store 가 이미 만들어져 있으면 즉시 반환하므로, 매 요청마다 호출해도
    실제 초기화 비용은 첫 요청 때 단 한 번만 발생한다.
    """
    global store, llm, chain
    if store is not None:        # 이미 준비됨 → 바로 종료
        return

    print(">>> [lazy init] 임베딩 / 벡터 스토어 / LLM 초기화 중...")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
        ("user", "{question}"),
    ])
    # 표준형(교재 4.1): RunnablePassthrough.assign 으로 context 추가, 입력 {"question": ...}
    retriever = store.as_retriever(search_kwargs={"k": 5})
    chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    print(">>> [lazy init] 초기화 완료")


def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


def add_pdf(file_path: str):
    """PDF 를 청킹해서 벡터 DB 에 추가"""
    _ensure_ready()
    
    docs   = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = os.path.basename(file_path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)


def answer_question(question: str) -> str:
    _ensure_ready()

    if store._collection.count() == 0:
        return "먼저 PDF를 업로드해주세요."
    # 검색+LLM 이 하나의 체인 → 입력은 {"question": ...}
    return chain.invoke({"question": question})


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
    # 지연 로딩이므로 reloader 를 켜둬도 시작이 즉시 끝난다.
    # (감시자 프로세스는 요청이 없어 초기화하지 않고,
    #  실제 서버도 첫 요청 때 한 번만 초기화한다.)
    app.run(debug=True, port=5001)


# 또는 시작 첫 요청이 느린걸 방지하려면 백그라운드 로딩.
# import threading
#
# def _warmup():
#     _ensure_ready()   # 백그라운드에서 미리 초기화
#
# if __name__ == "__main__":
#     # 리로더의 자식(실서버) 프로세스에서만 워밍업.
#     # (부모 감시자에서는 WERKZEUG_RUN_MAIN 이 없음 → 워밍업 안 함 → 여전히 1번)
#     if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#         threading.Thread(target=_warmup, daemon=True).start()
