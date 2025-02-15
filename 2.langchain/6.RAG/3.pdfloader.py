# pip install pypdf langchain-chroma

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(dotenv_path='../.env')

# PDF 파일 로드
pdf_filename = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
loader = PyPDFLoader(pdf_filename)
pages = loader.load()

print(f"총 페이지 수: {len(pages)}")
print(f"1페이지 내용 샘플:\n{pages[1].page_content}")

# 문서 분할
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
   separator="\n\n",
   chunk_size=2000,
   chunk_overlap=500,
)

texts = text_splitter.split_documents(pages)

# 임베딩 생성 및 Chroma DB 저장
embeddings = OpenAIEmbeddings()
store = Chroma.from_documents(
   texts, 
   embeddings, 
   collection_name="secure_coding_python",
   persist_directory="./DATA/chroma_db"
)

# ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 프롬프트 템플릿 생성
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 기술적 내용은 실제 예시를 포함하여 설명하세요
3. 보안 관련 내용은 위험성과 대응방안을 함께 설명하세요
4. 리스트 형태로 요청된 경우 번호를 매겨 구분하여 작성하세요
"""

prompt = ChatPromptTemplate.from_template(template)

# 검색 및 응답 체인 구성
retriever = store.as_retriever(search_kwargs={"k": 5})
chain = (
   {"context": retriever, "question": lambda x: x}
   | prompt
   | llm
   | StrOutputParser()
)

# 질문 함수
def ask_question(question):
   try:
       response = chain.invoke(question)
       print(f"\n질문: {question}")
       print(f"답변: {response}\n")
   except Exception as e:
       print(f"오류 발생: {str(e)}")

# 테스트 질문
ask_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")
ask_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")
