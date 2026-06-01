"""
Flask RAG 웹앱 #2 — 여러 문서 누적(append) + 문서 목록 표시.

문서 다루기 빌드업: #1 → #2 → #3
  #1 minimal      : PDF 1개 업로드 + 질문 (가장 단순)
  #2 file_append  : 여러 PDF 누적 + 목록 표시 + 부팅 시 기존 문서 로드  ← 여기
  #3 file_delete  : (#2 전부) + 문서 삭제

#1 과의 차등(이것만 추가됨, 나머지 코드는 #1 그대로):
  1) 여러 PDF 를 한 번에 / 계속 올리면 같은 벡터 DB 에 "누적"된다.   (upload: 여러 파일 처리)
  2) 벡터 DB 에 들어있는 문서 목록을 보여준다.                       (GET /files + list_documents)
  3) 같은 파일을 다시 올리면 중복 적재하지 않고 건너뛴다.            (add_pdf: source 중복 체크)

부팅 시 기존 문서가 보이는 이유:
  store 는 persist_directory("./chroma_db") 를 가리킨다. 즉 import 시점에
  Chroma(...) 를 만들면 디스크에 저장돼 있던 기존 벡터를 그대로 읽어온다.
  → 서버를 껐다 켜도 GET /files 가 예전에 넣은 문서를 그대로 보여준다.
  (별도 로딩 코드가 필요 없다 — Chroma 생성 자체가 곧 로딩이다.)
"""

import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

DATA_DIR        = "../DATA"         # 1~5 공유 (= 8.web_app/DATA)
PERSIST_DIR     = "../chroma_db"    # 벡터 DB 도 8.web_app 안에서 공유
COLLECTION_NAME = "rag_web"

os.makedirs(DATA_DIR, exist_ok=True)

# ─── 벡터 스토어 (전역) ────────────────────────────────
# persist_directory 를 주면, 이 객체를 만드는 순간 디스크의 기존 문서를 로드한다.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

# ─── RAG 체인 (표준 LCEL: 검색→프롬프트→LLM→파싱을 하나의 파이프라인으로) ───
retriever = store.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])

# 검색 단계(교재 4.2 retrieve_and_split 패턴): {"question"} → docs + 포맷된 context
def retrieve(inputs):
    docs = retriever.invoke(inputs["question"])
    return {"question": inputs["question"], "docs": docs, "context": format_docs(docs)}

# 전체 체인: 검색 → answer 를 assign (검색 docs 도 함께 반환 → 중간 결과 출력에 사용)
rag_chain = (
    RunnableLambda(retrieve)
    | RunnablePassthrough.assign(answer=(prompt | llm | StrOutputParser()))
)


# ─── #2 신규: 문서 목록 ────────────────────────────────
def _distinct_sources() -> dict:
    """벡터 DB 안의 문서별 청크 수를 {파일명: 청크수} 로 집계."""
    data = store._collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for m in data.get("metadatas", []):
        src = (m or {}).get("source", "(unknown)")
        counts[src] = counts.get(src, 0) + 1
    return counts


def list_documents() -> list[dict]:
    """벡터 DB 에 들어있는 문서 목록 (파일명 + 청크 수)."""
    return [{"source": s, "chunks": c}
            for s, c in sorted(_distinct_sources().items())]


def print_db_status():
    """시작 시 호출 — 기존 벡터 DB 에 어떤 문서가 들어있는지 콘솔에 출력.

    store(=Chroma) 는 위에서 생성되는 순간 persist_directory 의 기존 데이터를
    이미 읽어들였으므로, 여기서는 그 내용을 집계해 보여주기만 하면 된다.
    """
    docs = list_documents()
    total = sum(d["chunks"] for d in docs)
    print(f">>> [startup] 기존 벡터 DB 로드 — 문서 {len(docs)}건 / 청크 {total}개")
    if not docs:
        print("      (비어 있음 — 아직 업로드된 문서가 없습니다)")
    for d in docs:
        print(f"      - {d['source']} (청크 {d['chunks']}개)")


# import 시점(=서버 시작 시)에 현재 DB 상태를 한 번 출력
print_db_status()


def add_pdf(file_path: str) -> dict:
    """PDF 를 청킹해서 벡터 DB 에 추가. 이미 있는 문서면 건너뜀(#2 차등: 중복 방지)."""
    source = os.path.basename(file_path)
    if source in _distinct_sources():
        return {"source": source, "added": False}

    docs = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = source
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)
    return {"source": source, "added": True}


def answer_question(question: str) -> str:
    if store._collection.count() == 0:
        return "먼저 PDF를 업로드해주세요."
    
    # 검색+LLM 단일 파이프라인 실행 → {question, docs, context, answer}
    result = rag_chain.invoke({"question": question})
    docs = result["docs"]

    # ── 중간 결과: RAG 검색 결과를 터미널에 출력 ──
    print(f"\n>>> [RAG] 질문: {question}")
    print(f">>> [RAG] 검색된 청크 {len(docs)}개:")
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "?")
        page = d.metadata.get("page")
        page_str = f", p.{page + 1}" if isinstance(page, int) else ""
        snippet = d.page_content[:100].replace("\n", " ")
        print(f"    [{i}] {src}{page_str}\n        {snippet}...")

    return result["answer"]


# ─── Flask ─────────────────────────────────────────────
app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/files")
def files():
    """벡터 DB 에 적재된 문서 목록 — 페이지 로드/부팅 후 화면에 표시용."""
    return jsonify({"files": list_documents()})


@app.post("/upload")
def upload():
    # #2 차등: 여러 파일을 한 번에 받을 수 있게 getlist 사용
    uploaded = request.files.getlist("file")
    if not uploaded:
        return jsonify({"error": "파일이 없습니다"}), 400

    results = []
    for file in uploaded:
        if not file or not file.filename:
            continue
        path = os.path.join(DATA_DIR, file.filename)
        file.save(path)
        results.append(add_pdf(path))

    added   = [r["source"] for r in results if r["added"]]
    skipped = [r["source"] for r in results if not r["added"]]
    parts = []
    if added:
        parts.append(f"추가됨: {', '.join(added)}")
    if skipped:
        parts.append(f"건너뜀(중복): {', '.join(skipped)}")

    return jsonify({
        "message": " / ".join(parts) or "처리할 파일이 없습니다",
        "files": list_documents(),   # 갱신된 전체 목록을 함께 반환
    })


@app.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify({"answer": answer_question(question)})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
