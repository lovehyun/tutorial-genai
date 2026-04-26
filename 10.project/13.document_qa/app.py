# pip install flask openai chromadb langchain langchain-openai langchain-chroma langchain-community

import os
import json
from flask import Flask, request, jsonify, Response, render_template
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import openai

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader

load_dotenv()

# 1. 기본 설정
app = Flask(__name__)
app.secret_key = "document_qa_secret"

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
ALLOWED_EXTENSIONS = {"pdf", "txt"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 2. LangChain 컴포넌트 초기화
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate.from_template("""
다음 문서들을 참고하여 질문에 답변해주세요.
문서에 관련 내용이 없으면 "문서에서 관련 정보를 찾을 수 없습니다"라고 답변하세요.

문서들:
{context}

질문:
{question}
""")

chain = prompt | llm | StrOutputParser()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_vectorstore():
    """ChromaDB 벡터 저장소 가져오기 (없으면 생성)"""
    return Chroma(
        collection_name="document_qa",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

# 3. 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 4. 파일 업로드 및 임베딩
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "PDF 또는 TXT 파일만 지원합니다"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    try:
        # 파일 로드
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'pdf':
            loader = PyPDFLoader(filepath)
        else:
            loader = TextLoader(filepath, encoding='utf-8')

        documents = loader.load()

        # 메타데이터에 파일명 추가
        for doc in documents:
            doc.metadata["filename"] = filename

        # 텍스트 분할
        chunks = text_splitter.split_documents(documents)

        # 벡터 저장소에 추가
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

        return jsonify({
            "message": f"'{filename}' 업로드 완료",
            "chunks": len(chunks),
            "pages": len(documents),
        })

    except Exception as e:
        return jsonify({"error": f"파일 처리 중 오류: {str(e)}"}), 500

# 5. SSE 스트리밍 QA 엔드포인트
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "질문을 입력하세요"}), 400

    # 벡터 검색
    vectorstore = get_vectorstore()

    try:
        docs = vectorstore.similarity_search(question, k=3)
    except Exception:
        return jsonify({"error": "업로드된 문서가 없습니다. 먼저 문서를 업로드하세요."}), 400

    if not docs:
        return jsonify({"error": "관련 문서를 찾을 수 없습니다"}), 404

    context = "\n\n".join([f"[{doc.metadata.get('filename', '알 수 없음')}]\n{doc.page_content}" for doc in docs])
    sources = list(set(doc.metadata.get('filename', '알 수 없음') for doc in docs))

    def generate():
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "다음 문서들을 참고하여 질문에 답변하세요. 문서에 관련 내용이 없으면 '문서에서 관련 정보를 찾을 수 없습니다'라고 답변하세요. 한국어로 답변하세요."},
                    {"role": "user", "content": f"문서들:\n{context}\n\n질문: {question}"}
                ],
                stream=True,
                temperature=0,
                max_tokens=1000,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            # 소스 정보 전송
            yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# 6. 업로드된 문서 목록
@app.route('/documents', methods=['GET'])
def list_documents():
    if not os.path.exists(UPLOAD_DIR):
        return jsonify({"documents": []})

    files = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        size = os.path.getsize(filepath)
        files.append({
            "name": filename,
            "size": f"{size / 1024:.1f} KB",
        })

    return jsonify({"documents": files})

# 7. 문서 삭제
@app.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    filepath = os.path.join(UPLOAD_DIR, secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": f"'{filename}' 삭제 완료"})
    return jsonify({"error": "파일을 찾을 수 없습니다"}), 404

# 8. 실행
if __name__ == '__main__':
    print("=" * 50)
    print("문서 QA 웹 애플리케이션")
    print("=" * 50)
    print("브라우저에서 http://localhost:5000 접속")
    print(f"업로드 디렉토리: {UPLOAD_DIR}")
    print(f"벡터DB 디렉토리: {CHROMA_DIR}")
    print("-" * 50)
    app.run(debug=True)
