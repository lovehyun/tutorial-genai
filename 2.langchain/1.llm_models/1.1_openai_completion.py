# https://python.langchain.com/docs/get_started/introduction
# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                 0.3.15
# langchain-community       0.3.15
# langchain-core            0.3.31
# langchain-openai          0.2.14

import os
from dotenv import load_dotenv

# from langchain.llms import OpenAI  # 구버전
from langchain_openai import OpenAI  # 신버전


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'

load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")


# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)
llm = OpenAI(temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt) # 단일건 처리 = invoke
print(result)

# result = llm.generate([prompt]*5) # 다중건(batch) 처리 = generate
# for company_name in result.generations:
#     print(company_name[0].text)



# 기본 패키지 (langchain 설치 후)
# langchain==0.3.25
# langchain-core==0.3.59
# langchain-text-splitters==0.3.8

# LangChain 패키지 구조 요약 (v0.3.x 기준)
# 핵심 패키지: langchain
# 기본적인 체인, 프롬프트, 툴, 문서, 메모리 등의 추상 구조와 인터페이스 제공

# 주요 서브모듈
# 모듈	설명
# langchain_core	핵심 인터페이스, 타입, 에러 정의
# langchain.chains	LLMChain, RetrievalQAChain 등 체인 구성 로직
# langchain.prompts	PromptTemplate, ChatPromptTemplate 등
# langchain.memory	대화 기록 저장용 메모리 구조
# langchain.schema	메시지 구조, 응답 포맷, 문서 형식 등
# langchain.document_loaders	PDF, 웹페이지 등 문서 수집기
# langchain.embeddings	임베딩 처리기 인터페이스
# langchain.vectorstores	FAISS, Chroma 등 벡터 저장소 인터페이스
# langchain.agents	Tool + LLM + Planner 구성 자동화
# langchain.tools	계산기, 웹검색 등 툴 정의
# langchain.output_parsers	응답 결과를 정형 데이터로 파싱하는 도구

# 공급자별 연동 패키지 (langchain_openai, langchain_community, 등)
# LangChain v0.1.x까지는 모두 langchain 내부에 있었지만, v0.2~0.3부터는 다음처럼 외부 패키지로 분리되었습니다.
#
# 패키지명	설명
# langchain_openai	GPT-3.5, GPT-4, Embedding, Function calling 등
# langchain_community	다양한 커넥터(웹사이트, Weaviate, Pinecone 등)
# langchain_azure_openai	Azure OpenAI 전용 API 연동
# langchain_huggingface	HuggingFace Inference API 및 Pipeline 연동
# langchain_anthropic	Claude 모델 연동
# langchain_google_genai	Gemini 연동
# langchain_cohere	Cohere 모델 연동
