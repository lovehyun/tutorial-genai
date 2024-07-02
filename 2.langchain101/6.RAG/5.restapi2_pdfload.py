# curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d '{"question": "What is secure coding?"}'
# curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d "{\"question\": \"What is secure coding?\"}"

import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, pipeline

app = Flask(__name__)

# PDF 문서 경로
pdf_path = "./DATA/Python_SecureCoding_Guide.pdf"

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF document."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# PDF 문서에서 텍스트 추출
context = extract_text_from_pdf(pdf_path)

# 모델과 토크나이저를 로드하고 파이프라인을 설정합니다.
model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForQuestionAnswering.from_pretrained(model_name)
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    result = qa_pipeline(question=question, context=context)
    return jsonify({"answer": result['answer']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
