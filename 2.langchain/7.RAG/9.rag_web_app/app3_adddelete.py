# pip install flask flask-cors

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from database3 import (
    initialize_vector_db,
    initialize_components,
    create_vector_db, 
    answer_question, 
    get_store, 
    delete_file, 
    list_files,
    DATA_DIR,
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index3.html') 

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

# 업로드된 파일 목록 조회
@app.route('/files', methods=['GET'])
def get_file_list():
    files = list_files()
    return jsonify({"files": files}), 200

# 파일 삭제 (벡터 DB + 원본 파일)
@app.route('/files/<filename>', methods=['DELETE'])
def remove_file(filename):
    try:
        delete_file(filename)
        return jsonify({"message": f"'{filename}' 를 삭제했습니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    initialize_components()
    app.run(debug=True)
