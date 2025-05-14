# pip install flask flask-cors

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from vectordb import initialize_vector_db, create_vector_db, answer_question, get_store

app = Flask(__name__)
CORS(app)

VECTOR_DB_PATH = './vector_db.json'
DATA_DIR = './DATA'

# DATA 디렉토리가 존재하지 않으면 생성
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html') 

# 파일 업로드를 처리하는 엔드포인트
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    if file:
        file_path = os.path.join(DATA_DIR, file.filename)
        file.save(file_path)
        
        create_vector_db(file_path)
        return jsonify({"message": "파일이 업로드되고 벡터 DB가 성공적으로 생성되었습니다."}), 200

# 질문을 처리하는 엔드포인트
@app.route('/ask', methods=['POST'])
def ask_question():
    store = get_store()
    if store is None:
        return jsonify({"error": "벡터 데이터베이스가 로드되지 않았습니다. 먼저 문서를 업로드하세요."}), 400

    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400
    answer = answer_question(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    initialize_vector_db()
    app.run(debug=True)
