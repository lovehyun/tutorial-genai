from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
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

# 히스토리 유지 버전 (수동으로 메시지 관리)
def chat_with_history():
    print("챗봇과 대화를 시작합니다. (히스토리 유지)")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("="*50)
    
    # 메시지 히스토리 저장
    messages = []
    
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
            
            # 전체 대화 히스토리를 포함한 프롬프트 생성
            full_conversation = ""
            for msg in messages:
                full_conversation += f"{msg['role']}: {msg['content']}\n"
            full_conversation += f"Human: {user_input}\nAssistant:"
            
            # 프롬프트 템플릿으로 대화 히스토리 포함
            history_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Continue the conversation naturally based on the chat history."),
                ("human", full_conversation)
            ])
            
            history_chain = history_prompt | llm
            response = history_chain.invoke({"input": user_input})
            
            # 메시지 히스토리에 추가
            messages.append({"role": "Human", "content": user_input})
            messages.append({"role": "Assistant", "content": response.content})
            
            print(f"\n챗봇: {response.content}")
            print("-"*30)
            
        except Exception as error:
            print(f"오류가 발생했습니다: {str(error)}")

# LangChain Memory를 사용한 고급 버전
def chat_with_langchain_memory():
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    
    print("챗봇과 대화를 시작합니다. (LangChain Memory 사용)")
    print("명령어:")
    print("  - 'quit' 또는 'exit': 종료")
    print("  - 'clear': 대화 히스토리 초기화")
    print("  - 'history': 대화 히스토리 보기")
    print("="*50)
    
    # 메모리 설정
    memory = ConversationBufferMemory()
    
    # 대화 체인 생성 (메모리 포함)
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False  # True로 설정하면 내부 처리 과정을 볼 수 있음
    )
    
    while True:
        user_input = input("\n당신: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', '끝']:
            print("대화를 종료합니다. 안녕히 가세요!")
            break
        
        if user_input.lower() in ['clear', '초기화']:
            memory.clear()
            print("대화 히스토리가 초기화되었습니다.")
            continue
        
        if user_input.lower() in ['history', '히스토리']:
            print("\n=== 대화 히스토리 ===")
            print(memory.buffer)
            print("==================")
            continue
        
        if not user_input:
            print("메시지를 입력해주세요.")
            continue
        
        try:
            print("\n챗봇이 응답을 생성중입니다...")
            response = conversation.predict(input=user_input)
            print(f"\n챗봇: {response}")
            print("-"*30)
            
        except Exception as error:
            print(f"오류가 발생했습니다: {str(error)}")

# 커스텀 프롬프트가 포함된 고급 버전
def chat_with_custom_prompt():
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    
    print("챗봇과 대화를 시작합니다. (커스텀 프롬프트)")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("="*50)
    
    # 커스텀 프롬프트 템플릿
    template = """당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 
사용자와 자연스럽게 대화하며, 질문에 정확하고 유용한 답변을 제공해주세요.

현재까지의 대화:
{history}

사용자: {input}
어시스턴트:"""
    
    custom_prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )
    
    memory = ConversationBufferMemory()
    
    conversation = ConversationChain(
        llm=llm,
        prompt=custom_prompt,
        memory=memory,
        verbose=False
    )
    
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
            response = conversation.predict(input=user_input)
            print(f"\n챗봇: {response}")
            print("-"*30)
            
        except Exception as error:
            print(f"오류가 발생했습니다: {str(error)}")

if __name__ == "__main__":
    # 원하는 버전을 선택해서 실행
    
    # 1. 기본 버전 (히스토리 없음)
    # simple_chat()
    
    # 2. 수동 히스토리 관리 버전
    # chat_with_history()
    
    # 3. LangChain Memory 사용 버전 (권장)
    # chat_with_langchain_memory()
    
    # 4. 커스텀 프롬프트 버전
    chat_with_custom_prompt()
    
    # 간단한 테스트를 원한다면:
    # print(chat("Hello"))
    # print(chat("Can we talk about sports?"))
    # print(chat("What's a good sport to play outdoor?"))
