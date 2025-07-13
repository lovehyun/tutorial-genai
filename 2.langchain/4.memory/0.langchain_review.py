from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# 프롬프트 템플릿 생성
prompt_template = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# 올드 스타일 방법들

def chat_old_style_1(message):
    """방법 1: 프롬프트 템플릿을 수동으로 포맷팅"""
    # 프롬프트 템플릿에 값 채우기
    formatted_prompt = prompt_template.format(input=message)
    
    # LLM에 직접 전달
    response = llm.invoke(formatted_prompt)
    return response.content

def chat_old_style_2(message):
    """방법 2: 프롬프트 템플릿의 format_messages 사용"""
    # 프롬프트를 메시지 형태로 포맷팅
    messages = prompt_template.format_messages(input=message)
    
    # LLM에 메시지 전달
    response = llm.invoke(messages)
    return response.content

def chat_old_style_3(message):
    """방법 3: 직접 메시지 객체 생성"""
    # HumanMessage 직접 생성
    human_message = HumanMessage(content=message)
    
    # LLM에 메시지 리스트 전달
    response = llm.invoke([human_message])
    return response.content

def chat_old_style_4(message):
    """방법 4: 완전 수동 방식 (가장 올드)"""
    # 프롬프트 템플릿 없이 직접 문자열 처리
    messages = [
        {"role": "user", "content": message}
    ]
    
    # OpenAI 클라이언트 직접 사용하는 것처럼
    response = llm.invoke(messages)
    return response.content

def chat_with_system_message_old(message):
    """시스템 메시지 포함 올드 스타일"""
    from langchain_core.messages import SystemMessage, HumanMessage
    
    # 시스템 메시지와 사용자 메시지 직접 생성
    system_msg = SystemMessage(content="You are a helpful assistant.")
    human_msg = HumanMessage(content=message)
    
    # 메시지 리스트로 전달
    response = llm.invoke([system_msg, human_msg])
    return response.content


# 새로운 스타일과 비교를 위한 함수
def chat_new_style(message):
    """새로운 스타일 (LCEL - LangChain Expression Language)"""
    chain = prompt_template | llm
    response = chain.invoke({"input": message})
    return response.content

def main():
    """각 방법들을 테스트"""
    test_message = "Hello, how are you?"
    
    print("=== 올드 스타일 방법들 ===\n")
    
    print("방법 1 (프롬프트 format):")
    print(chat_old_style_1(test_message))
    print()
    
    print("방법 2 (format_messages):")
    print(chat_old_style_2(test_message))
    print()
    
    print("방법 3 (직접 메시지 객체):")
    print(chat_old_style_3(test_message))
    print()
    
    print("방법 4 (완전 수동):")
    print(chat_old_style_4(test_message))
    print()
    
    print("시스템 메시지 포함:")
    print(chat_with_system_message_old(test_message))
    print()
    
    print("=== 비교: 새로운 스타일 ===")
    print("새로운 스타일 (LCEL):")
    print(chat_new_style(test_message))
    print()


# 실제 대화 테스트 (올드 스타일 사용)
def test_conversation():
    """대화 테스트"""
    print("=== 대화 테스트 (올드 스타일 방법 2 사용) ===")
    
    messages = [
        "Hello",
        "Can we talk about sports?", 
        "What's a good sport to play outdoor?"
    ]
    
    for msg in messages:
        print(f"사용자: {msg}")
        response = chat_old_style_2(msg)
        print(f"AI: {response}")
        print("-" * 50)

if __name__ == "__main__":
    # 모든 방법 테스트
    main()
    
    # 대화 테스트
    test_conversation()
    

# 참고: 올드 스타일 vs 새로운 스타일:

# 올드 스타일:
# - prompt_template.format_messages(input=message)
# - llm.invoke(messages)
# - 단계별로 명시적 처리

# 새로운 스타일 (LCEL):
# - chain = prompt | llm
# - chain.invoke({"input": message})
# - 파이프라인으로 간결하게 연결

# 가장 일반적인 올드 스타일: 방법 2 (format_messages)
