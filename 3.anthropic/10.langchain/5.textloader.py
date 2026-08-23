import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
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

# LCEL 체인으로 요약
summary_prompt = PromptTemplate.from_template(
    "다음 텍스트를 간결하게 요약해주세요:\n\n{text}"
)
chain = summary_prompt | llm | StrOutputParser()

if docs:
    summary = chain.invoke({"text": docs[0].page_content})
    print("첫 번째 청크 요약:")
    print(summary)
