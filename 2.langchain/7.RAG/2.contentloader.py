from dotenv import load_dotenv

# 대화 라이브러리
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# 임베딩 라이브러리
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# LangChain의 커뮤니티 통합 모듈 안에 있는 Chroma 래퍼 (Legacy)
# pip install langchain-community chromadb tiktoken
# from langchain_community.vectorstores import Chroma

# LangChain 0.2 이후부터 권장되는 신규 모듈 구조
# pip install langchain-chroma chromadb
from langchain_chroma import Chroma



# 1. .env 파일에서 OPENAI_API_KEY 등 환경 변수 로드
load_dotenv(dotenv_path='../.env')

# 2. 문서 로드 (euc-kr로 인코딩된 텍스트 파일)
# Windows에서 cp949 디코딩 오류를 방지하려면 euc-kr로 저장해야 함
loader = TextLoader('./nvme.txt', encoding='utf-8')  # utf-8 또는 euc-kr
documents = loader.load()

# 3. 문서를 1000자 단위로 분할하고 200자 중복 유지 - 1000개 단어 vs 1000개 토큰
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 4. 텍스트 조각을 임베딩으로 변환하기 위한 OpenAI 임베딩 모델 준비
embeddings = OpenAIEmbeddings()

# 5. Chroma 벡터 저장소 생성 및 임베딩 저장 (collection 이름 지정)
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

# 6. GPT-3.5 기반 언어 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 7. 벡터DB에서 연관 문서를 검색할 수 있는 retriever 구성
retriever = store.as_retriever()

# 8. 질문과 context를 기반으로 응답을 생성할 프롬프트 템플릿 정의
template = """다음 컨텍스트를 사용하여 질문에 답변해주세요:

{context}

질문: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 9. 체인 구성
def peek_prompt(prompt_value):
    print("=== LLM 직전 프롬프트 ===")
    print(prompt_value.to_string())
    return prompt_value  # 반드시 그대로 반환해서 체인이 계속 흘러가게 함

# - "사용자 질문" 은 그대로 "question"에 들어가고
# - retriever가 context를 검색하여 "context"에 전달
chain1 = (
    {"context": retriever, "question": RunnablePassthrough()} # RunnablePassThrough() 는 lambda x: x 와 동일
    | prompt 
    | llm
)

chain2_debug = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt 
    | RunnableLambda(peek_prompt)  # <- 여기서 디버깅용 프린트
    | llm
)

to_text = RunnableLambda(lambda docs: "\n\n---\n\n".join(d.page_content for d in docs))
chain3_contents = (
    {"context": retriever | to_text, "question": RunnablePassthrough()}
    | prompt
    | RunnableLambda(peek_prompt)  # <- 여기서 디버깅용 프린트
    | llm
)

# 10. 실제 질문 실행
question = "NVME와 SATA의 차이점을 100글자로 요약해줘"

# 10-1. context(검색된 문서)만 미리 확인
# context_docs = retriever.invoke(question)
# print("=== 검색된 문서(Context) ===")
# for i, doc in enumerate(context_docs, start=1):
#     print(f"[Chunk{i}] {doc.page_content}\n")
# print("=== 검색된 문서 끝 ===\n")

# 10-2. 체인을 통해 질문 실행
# response = chain1.invoke(question)
# response = chain2_debug.invoke(question)
response = chain3_contents.invoke(question)

# 11. 응답 출력
print(response.content)
