# pip install tqdm

import os
import fitz  # PyMuPDF
import re
from flask import Flask, request, jsonify
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, pipeline
import concurrent.futures
from tqdm import tqdm

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

def preprocess_text(text):
    """Preprocess the text for better efficiency."""
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    # 특수 문자 제거
    text = re.sub(r'[^A-Za-z0-9가-힣\s]', '', text)
    # 한글만 남기기
    # text = re.sub(r'[^가-힣\s]', '', text)
    # 텍스트 정규화
    text = text.lower()
    return text

def split_text_into_chunks(text, max_length):
    """Split the text into chunks of maximum length."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_chunk(chunk, question, qa_pipeline):
    """Process a single chunk with the question."""
    result = qa_pipeline(question=question, context=chunk)
    return result['answer']

# PDF 문서에서 텍스트 추출 및 전처리
context = extract_text_from_pdf(pdf_path)
print(context)
print('-' * 50)
context = preprocess_text(context)
print(context)
print('-' * 50)

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

    max_chunk_length = 512  # 모델이 처리할 수 있는 최대 토큰 수
    chunks = split_text_into_chunks(context, max_chunk_length)

    answers = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_chunk, chunk, question, qa_pipeline) for chunk in chunks]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing chunks"):
            answer = future.result()
            answers.append(answer)
            print(f"Chunk Answer: {answer}")  # 각 청크의 답변을 출력

    # 모든 답변을 출력
    print(f"All Answers: {answers}")

    # 가장 빈번하게 등장하는 답변 선택 (다수결 방식)
    final_answer = max(set(answers), key=answers.count)
    return jsonify({"answer": final_answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
