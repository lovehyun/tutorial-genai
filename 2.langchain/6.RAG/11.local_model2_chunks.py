# pip install transformers pymupdf
import fitz  # PyMuPDF
from typing import List, Optional
from collections import Counter
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# PDF 문서에서 텍스트를 추출한 뒤, 내용을 여러 조각으로 나눠서(Chunking) DistilBERT 기반 QA 모델로 질문에 답변을 생성하는 프로그램입니다.
# - 앞서 보여주신 이전 코드보다 한 단계 업그레이드된 형태이고, 
# - 핵심 의도는 긴 PDF 문서를 모델이 처리 가능한 길이로 나누어 각 조각별로 답변을 구하고, 
# - 그중 가장 많이 나온 답변을 최종 결과로 선택하는 방식입니다.

# 각 청크별 답변을 모아 빈도수 높은 것을 최종 선택
# 전체 단어 수, 청크 수, 각 청크별 답변을 출력

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

def split_text_into_chunks(text: str, max_length: int) -> List[str]:
   """텍스트를 지정된 최대 길이의 청크로 분할합니다."""
   words = text.split()
   chunks = []
   current_chunk = []
   current_length = 0

   for word in words:
       # 현재 단어를 추가했을 때 최대 길이를 초과하는 경우
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

def answer_question(qa_pipeline: pipeline, question: str, context: str) -> str:
   """주어진 컨텍스트를 기반으로 질문에 답변합니다."""
   try:
       # 모델의 최대 입력 길이에 맞게 텍스트 분할
       max_chunk_length = 512
       chunks = split_text_into_chunks(context, max_chunk_length)

       # 컨텍스트 분석 정보 출력
       context_length = len(context.split())
       print(f"전체 컨텍스트 길이 (단어 수): {context_length}")
       print(f"청크 수: {len(chunks)}")
       
       # 각 청크에 대해 답변 생성
       answers = []
       for i, chunk in enumerate(chunks, 1):
           result = qa_pipeline(question=question, context=chunk)
           answers.append(result['answer'])
           print(f"청크 {i} 답변: {result['answer']}")
           print('-' * 50)

       # 가장 빈번한 답변 선택 (Counter 사용)
       if not answers:
           return "답변을 생성할 수 없습니다."
           
       final_answer = Counter(answers).most_common(1)[0][0]
       return final_answer
       
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

   # 질문 처리
   question = "시큐어 코딩이란?"
   print(f"\n질문: {question}")
   answer = answer_question(qa_pipeline, question, context)
   print(f"최종 답변: {answer}")

if __name__ == "__main__":
   main()
