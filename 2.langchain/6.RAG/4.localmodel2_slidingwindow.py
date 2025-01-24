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

def answer_question(qa_pipeline, question, context):
    """Answer a question based on the provided context."""
    max_chunk_length = 512  # 모델이 처리할 수 있는 최대 토큰 수
    chunks = split_text_into_chunks(context, max_chunk_length)

    # 전체 context 길이 출력
    context_length = len(context.split())
    print(f"Total context length (in words): {context_length}")
    
    # 각 청크 길이와 총 청크 수 출력
    num_chunks = len(chunks)
    print(f"Number of chunks: {num_chunks}")
        
    answers = []
    for chunk in chunks:
        result = qa_pipeline(question=question, context=chunk)
        answers.append(result['answer'])
        print(result['answer'])
        print('-' * 50)

    # 가장 빈번하게 등장하는 답변 선택 (다수결 방식)
    final_answer = max(set(answers), key=answers.count)
    return final_answer

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
