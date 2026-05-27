# pip install transformers pymupdf
import fitz  # PyMuPDF
from typing import Optional
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# 모델 설명
# - DistilBERT: BERT를 경량화(distillation)한 모델 → 속도는 빠르고, 메모리 사용량이 적음.
# - base-uncased: 영어 소문자 기반 토크나이저(대소문자 구분 안 함).
# - distilled-squad: SQuAD(Stanford Question Answering Dataset) 데이터셋으로 파인튜닝된 질의응답(QA) 전용 모델.
# - 용도: 문맥(context)과 질문(question)을 입력하면, 해당 문맥에서 가장 가능성이 높은 답변 구간을 찾아 반환.

# PDF 전체를 한 번에 모델에 넣음 → 토큰 제한 걸릴 수 있음
# 첫 번째 답변만 사용	

def extract_text_from_pdf(pdf_path: str) -> str:
   """PDF 문서에서 텍스트를 추출합니다."""
   try:
       doc = fitz.open(pdf_path)
       text_parts = []
       
       for page_num in range(doc.page_count):
           page = doc.load_page(page_num)
           text_parts.append(page.get_text())
           
       doc.close()
       return "\n\n".join(text_parts)
   except Exception as e:
       print(f"PDF 텍스트 추출 중 오류 발생: {str(e)}")
       return ""

def setup_qa_pipeline() -> Optional[pipeline]:
   """DistilBERT를 사용하여 QA 파이프라인을 설정합니다."""
   try:
       model_name = "distilbert-base-uncased-distilled-squad"
       tokenizer = AutoTokenizer.from_pretrained(model_name)
       model = AutoModelForQuestionAnswering.from_pretrained(model_name)
       return pipeline("question-answering", model=model, tokenizer=tokenizer)
   except Exception as e:
       print(f"QA 파이프라인 설정 중 오류 발생: {str(e)}")
       return None

def answer_question(qa_pipeline: pipeline, question: str, context: str) -> str:
   """주어진 컨텍스트를 기반으로 질문에 답변합니다."""
   try:
       result = qa_pipeline(question=question, context=context)
       return result['answer']
   except Exception as e:
       return f"답변 생성 중 오류 발생: {str(e)}"

def main():
   # PDF 경로 설정
   pdf_path = "./DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf"
   
   # PDF에서 텍스트 추출
   print("PDF에서 텍스트를 추출하는 중...")
   context = extract_text_from_pdf(pdf_path)
   if not context:
       print("PDF에서 텍스트를 추출할 수 없습니다.")
       return
   
   print(f"추출된 텍스트 길이: {len(context)} 문자")
   print("텍스트 샘플:", context[:500], "...")
   print('-' * 50)

   # QA 파이프라인 설정
   print("QA 파이프라인을 설정하는 중...")
   qa_pipeline = setup_qa_pipeline()
   if not qa_pipeline:
       print("QA 파이프라인을 설정할 수 없습니다.")
       return

   # 질문 목록
   questions = [
       "시큐어 코딩이란?",
       "입력 데이터 검증은 어떻게 해야 하나요?",
       "주요 보안 취약점은 무엇인가요?"
   ]

   # 각 질문에 대한 답변 생성
   print("\n질문 및 답변:")
   for question in questions:
       print(f"\n질문: {question}")
       answer = answer_question(qa_pipeline, question, context)
       print(f"답변: {answer}")

if __name__ == "__main__":
   main()
