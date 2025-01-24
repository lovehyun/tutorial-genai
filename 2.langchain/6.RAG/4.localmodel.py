# pip install transformers pymupdf

import fitz  # PyMuPDF
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, pipeline

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF document."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def setup_qa_pipeline():
    """Set up the QA pipeline using DistilBERT."""
    model_name = "distilbert-base-uncased-distilled-squad"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForQuestionAnswering.from_pretrained(model_name)
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
    return qa_pipeline

def answer_question(qa_pipeline, question, context):
    """Answer a question based on the provided context."""
    result = qa_pipeline(question=question, context=context)
    return result['answer']

def main():
    # PDF 문서에서 텍스트 추출
    pdf_path = "./DATA/Python_SecureCoding_Guide.pdf"
    context = extract_text_from_pdf(pdf_path)
    print(context)
    print('-' * 50)

    # QA 파이프라인 설정
    qa_pipeline = setup_qa_pipeline()

    # 예제 질문 수행
    question = "시큐어 코딩이란?"
    answer = answer_question(qa_pipeline, question, context)
    print(f"Question: {question}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
