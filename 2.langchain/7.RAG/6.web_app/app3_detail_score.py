# pip install flask flask-cors

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from services.vectorstore3 import initialize_vector_db, create_vector_db, DATA_DIR
from services.qa_service3 import answer_question, answer_question_score

app = Flask(__name__, static_url_path="")
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

# 질문을 처리하는 엔드포인트
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400

    # answer = answer_question(question)
    answer = answer_question_score(question)

    return jsonify({"answer": answer})

if __name__ == '__main__':
    initialize_vector_db()
    app.run(debug=True)
