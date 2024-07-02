# pip install pypdf

from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

from langchain_community.document_loaders import PyPDFLoader

pdf_filename = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
loader = PyPDFLoader(pdf_filename)
pages = loader.load()

print(len(pages))

# print(pages[1])
print(pages[1].page_content)

# 이전과 동일...

load_dotenv(dotenv_path='../.env')

documents = loader.load()

# 파라그래프, 라인, 단어, 형태로 구분해서 잘라서 저장
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    separator="\n\n", # 분할기준
    chunk_size=2000,  # 사이즈
    chunk_overlap=500, # 중첩 사이즈
)

# 분할 실행
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

# 오픈소스 임베딩DB 인 Chroma 사용해서 데이터 저장
store = Chroma.from_documents(texts, embeddings, collection_name="secure_coding_python")

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
chain = RetrievalQA.from_chain_type(llm, retriever=store.as_retriever())

print(chain.invoke("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")['result'])
print(chain.invoke("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")['result'])
