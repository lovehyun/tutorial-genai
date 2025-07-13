from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# 또는 프롬프트 템플릿 생성 - HumanMessagePromptTemplate 사용
prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{input}")
])
# 대화 체인 생성 - 메모리가 연결되지 않음
chain = prompt | llm

# 기본 채팅 함수
def chat(message):
    response = chain.invoke({"input": message})
    return response.content


# 기본 사용자 인터랙션
def simple_chat():
    print("챗봇과 대화를 시작합니다. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("="*50)
    
    while True:
        user_input = input("\n당신: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', '끝']:
            print("대화를 종료합니다. 안녕히 가세요!")
            break
        
        if not user_input:
            print("메시지를 입력해주세요.")
            continue
        
        try:
            print("\n챗봇이 응답을 생성중입니다...")
            response = chat(user_input)
            print(f"\n챗봇: {response}")
            print("-"*30)
        except Exception as error:
            print(f"오류가 발생했습니다: {str(error)}")

if __name__ == "__main__":
    # 원하는 버전을 선택해서 실행
    
    # 1. 기본 버전 (히스토리 없음)
    simple_chat()
