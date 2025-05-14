# pip install chromadb tiktoken

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import Chroma

# 1. .env 파일에서 OpenAI API 키 불러오기
load_dotenv(dotenv_path='../.env')

# 2. 문서 로드 (euckr 인코딩으로 읽기)
loader = TextLoader('./nvme.txt', encoding='euckr')
documents = loader.load()

# 3. 각 문서에 출처 메타데이터 추가 (출처 추적용)
documents = [Document(page_content=doc.page_content, metadata={"source": "nvme.txt"}) for doc in documents]

# 4. 문서를 적절한 크기로 분할 (1000자 단위, 100자 중복 유지, 메타데이터 자동 유지됨)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# 5. 문서 청크에 대한 벡터 임베딩 생성
embeddings = OpenAIEmbeddings()

# 6. 벡터 저장소에 저장 (Chroma 사용)
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

# 7. GPT-3.5 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 8. 답변에 문서 출처 포함하도록 프롬프트 정의
template = """다음 문서들을 참고하여 질문에 답변해주세요. 
출처도 반드시 포함해주세요.

문서들: {context}

질문: {question}

답변을 작성하고 마지막에 "출처: " 다음에 참고한 문서의 출처를 명시해주세요.
"""
prompt = ChatPromptTemplate.from_template(template)

# 9. 문서 검색 + LLM 응답 체인 구성
retriever = store.as_retriever(search_kwargs={"k": 5})  # 유사도 기준 상위 5개 문서 검색
chain = (
   {"context": retriever, "question": lambda x: x}  # context는 retriever가 채움, question은 그대로 전달
   | prompt
   | llm
   | StrOutputParser()  # 응답을 문자열로 처리 (최종 result.context 부분을 문자열로 반환)
)

# 10. 질문을 받아 응답 + 출처를 분리해서 반환하는 함수
def answer_question(question):
   try:
       result = chain.invoke(question)  # LLM 체인 실행

       # '출처:' 기준으로 응답과 출처 분리
       if "출처:" in result:
           answer, sources = result.split("출처:", 1)
           answer = answer.strip()
           sources = sources.strip()
       else:
           answer = result.strip()
           sources = "출처 정보를 찾을 수 없습니다."

       # 의미 없는 답변 처리
       if not answer or answer.lower() == "i don't know.":
           return f"질문: {question}\n응답: 이 질문에 대한 답변을 제공할 수 없습니다.\n"
       
       return f"질문: {question}\n응답: {answer}\n출처: {sources}\n"
       
   except Exception as e:
       return f"질문: {question}\n응답: 오류가 발생했습니다: {str(e)}\n"

# 11. 테스트 질문 실행
print(answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘"))
print(answer_question("PCIe는?"))
print(answer_question("우주의 크기는 얼마나 되나요?"))
