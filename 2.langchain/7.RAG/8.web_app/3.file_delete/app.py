"""
Flask RAG 웹앱 #3 — 문서 삭제(delete) 기능 추가. 문서 다루기 완성판.

문서 다루기 빌드업: #1 → #2 → #3
  #1 minimal      : PDF 1개 업로드 + 질문 (가장 단순)
  #2 file_append  : 여러 PDF 누적 + 목록 표시 + 부팅 시 기존 문서 로드
  #3 file_delete  : (#2 전부) + 문서 삭제  ← 여기

#2 와의 차등(이것만 추가됨, 나머지 코드는 #2 그대로):
  1) delete_document() — 해당 문서의 벡터 청크 + 원본 PDF 파일을 함께 삭제
  2) DELETE /files/<파일명> 라우트
  3) 화면의 문서 목록 각 항목에 "삭제" 버튼

삭제의 핵심:
  벡터를 넣을 때 metadata["source"] = 파일명 을 박아두었으므로,
  store._collection.delete(where={"source": 파일명}) 으로 그 문서의
  청크들만 골라서 지운다. 원본 PDF 파일(DATA_DIR)도 같이 정리한다.
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
# persist_directory 를 주면, 이 객체를 만드는 순간 디스크의 기존 문서를 로드한다.
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


def add_pdf(file_path: str) -> dict:
    """PDF 를 청킹해서 벡터 DB 에 추가. 이미 있는 문서면 건너뜀."""
    source = os.path.basename(file_path)
    if source in _distinct_sources():
        return {"source": source, "added": False}

    docs = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = source
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)
    return {"source": source, "added": True}


def delete_document(source: str) -> bool:
    """#3 차등: 문서 1건 삭제 — 벡터(해당 source 청크) + 원본 PDF 파일.

    반환: 실제로 벡터 DB 에 있던 문서였으면 True, 없었으면 False.
    """
    existed = source in _distinct_sources()

    # 1) 벡터 삭제 — metadata.source 가 일치하는 청크들만
    store._collection.delete(where={"source": source})

    # 2) 원본 파일 삭제 (있으면)
    # path = os.path.join(DATA_DIR, source)
    # if os.path.exists(path):
    #     os.remove(path)

    return existed


def reset_db() -> int:
    """DB 초기화 — 컬렉션의 모든 청크를 삭제(전체 비우기). 삭제한 청크 수 반환."""
    ids = store._collection.get().get("ids", [])
    if ids:
        store._collection.delete(ids=ids)
    return len(ids)


def answer_question(question: str) -> str:
    if store._collection.count() == 0:
        return "먼저 PDF를 업로드해주세요."
    # 문서 구분 없이 전체 컬렉션에서 통합 검색 (여러 문서를 함께 참조)
    docs = store.similarity_search(question, k=5)

    # ── 중간 결과: RAG 검색 결과를 터미널에 출력 ──
    print(f"\n>>> [RAG] 질문: {question}")
    print(f">>> [RAG] 검색된 청크 {len(docs)}개:")
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "?")
        page = d.metadata.get("page")
        page_str = f", p.{page + 1}" if isinstance(page, int) else ""
        snippet = d.page_content[:100].replace("\n", " ")
        print(f"    [{i}] {src}{page_str}\n        {snippet}...")

    context = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"context": context, "question": question})


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
        "files": list_documents(),
    })


# ─── #3 신규: 문서 삭제 ────────────────────────────────
@app.delete("/files/<path:source>")
def remove_file(source):
    try:
        existed = delete_document(source)
        msg = f"'{source}' 삭제 완료" if existed else f"'{source}' 은(는) 목록에 없었습니다"
        return jsonify({"message": msg, "files": list_documents()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/reset")
def reset():
    """DB 초기화 — 벡터 DB 에 든 모든 문서를 한 번에 삭제."""
    try:
        n = reset_db()
        return jsonify({"message": f"DB 초기화 완료 (청크 {n}개 삭제)", "files": list_documents()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify({"answer": answer_question(question)})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
