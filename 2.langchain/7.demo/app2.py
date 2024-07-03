# pip install flask flask-cors pypdf

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from ai_model2 import create_vector_db, answer_question, load_vector_dbs, DATA_DIR, VECTOR_DB_DIR

app = Flask(__name__)
CORS(app)

# DATA 디렉토리가 존재하는지 확인하고, 존재하지 않으면 생성
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

stores = None  # DB 로딩 안된 초기 상태

@app.route('/upload', methods=['POST'])
def upload_file():
    global stores

    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다."}), 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    is_pdf = file_ext == '.pdf'
    file_path = os.path.join(DATA_DIR, file.filename)

    if file:
        file.save(file_path)
        stores = create_vector_db(file_path, os.path.splitext(file.filename)[0], is_pdf)
        return jsonify({"message": "파일이 업로드되고 벡터 DB가 성공적으로 생성되었습니다."}), 200

@app.route('/ask', methods=['POST'])
def ask_question_route():
    global stores
    if stores is None:
        return jsonify({"error": "벡터 데이터베이스가 로드되지 않았습니다. 먼저 문서를 업로드하세요."}), 400

    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400
    
    answer = answer_question(question)
    print(f"{answer}")

    # \n을 <br>로 변환
    formatted_answer = answer.replace('\n', '<br>')

    return jsonify({"answer": formatted_answer})

@app.route('/')
def index():
    return send_from_directory('./static', 'index2.html')

if __name__ == '__main__':
    # 벡터 데이터베이스 파일이 존재하면 로드
    if os.path.exists(VECTOR_DB_DIR):
        stores = load_vector_dbs()
    app.run(debug=True)
