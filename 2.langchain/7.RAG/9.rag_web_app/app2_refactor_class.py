# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from services.vectorstore2 import VectorStore, DATA_DIR
from services.qa_service2 import QAService

app = Flask(__name__)
CORS(app)

db = VectorStore()
db.initialize()
chatbot = QAService(db)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    file_path = os.path.join(DATA_DIR, file.filename)
    file.save(file_path)
    
    db.add_pdf(file_path)
    return jsonify({"message": "파일 업로드 및 벡터 DB 갱신 완료"}), 200

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400
    
    answer = chatbot.answer(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
