# pip install flask flask-cors
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from services.vectorstore4 import (
    initialize_vector_db,
    create_vector_db, 
    delete_file, 
    list_files,
    DATA_DIR,
)

from services.qa_service4 import (
    initialize_llm,
    answer_question,
    answer_question_score
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index4.html') 

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
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400
        
    answer = answer_question(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    initialize_vector_db()
    initialize_llm()
    app.run(debug=True)
