import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 텍스트 파일 로드
loader = TextLoader("my_document.txt", encoding="utf-8")
documents = loader.load()

# 텍스트 분할
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200
)
docs = text_splitter.split_documents(documents)

print(f"문서가 {len(docs)}개의 청크로 분할되었습니다.")

# 첫 번째 청크에 대한 요약 생성
summary_template = PromptTemplate(
    input_variables=["text"],
    template="다음 텍스트를 간결하게 요약해주세요:\n\n{text}"
)

summary_chain = LLMChain(llm=llm, prompt=summary_template)
if docs:
    summary = summary_chain.invoke({"text": docs[0].page_content})
    print("첫 번째 청크 요약:")
    print(summary["text"])
