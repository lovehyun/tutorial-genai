import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# 메모리 관리용 클래스
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

import logging
from langchain_core.callbacks import CallbackManager, StdOutCallbackHandler

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my_secret_key')

load_dotenv('../.env')

# OpenAI API 키 설정
openai_api_key = os.environ.get('OPENAI_API_KEY')

# 각 학년별 커리큘럼 데이터
curriculums = {
    1: ["기초 인사", "간단한 문장", "동물 이름"],
    2: ["학교 생활", "가족 소개", "자기 소개"],
    3: ["취미와 운동", "날씨 묘사", "간단한 이야기"],
    4: ["쇼핑과 가격", "음식 주문", "여행 이야기"],
    5: ["역사와 문화", "과학과 자연", "사회 이슈"],
    6: ["미래 계획", "진로 탐색", "세계 여행"]
}

# 사용자별 채팅 기록 저장소
chat_histories = {}

def print_chat_history(history_id):
    """특정 히스토리의 모든 메시지를 출력"""
    if history_id in chat_histories:
        history = chat_histories[history_id]
        messages = history.messages
        
        logger.info(f"\n===== 대화 기록 (ID: {history_id}) =====")
        for i, msg in enumerate(messages):
            role = "시스템" if isinstance(msg, SystemMessage) else "학생" if isinstance(msg, HumanMessage) else "교사"
            logger.info(f"{i+1}. {role}: {msg.content}")
        logger.info("=" * 40)
        
# 채팅 기록 가져오기 함수
def get_chat_history(user_id, grade, curriculum_title) -> BaseChatMessageHistory:
    """특정 사용자, 학년, 커리큘럼에 대한 채팅 기록 반환"""
    history_id = f"{user_id}_{grade}_{curriculum_title}"
    
    if history_id not in chat_histories:
        chat_histories[history_id] = ChatMessageHistory()
    
    return chat_histories[history_id]

# 시스템 프롬프트 생성 함수
def create_system_prompt(grade, curriculum_title):
    """특정 학년과 커리큘럼에 맞는 시스템 프롬프트 생성"""
    return (
        f"당신은 초등학교 {grade}학년 학생을 위한 영어 교사입니다. "
        f"학생이 {curriculum_title}에 대해 학습할 수 있도록 도와주세요. "
        f"학생이 한국말로 문의를 하더라도 영어로 다시 해당 한국어에 대해서 질문을 할 수 있도록 답변을 유도해야 합니다. "
        f"학생이 영어를 못하는 경우에는 한국말로 설명을 하면서 영어를 가르쳐주세요. "
        f"예를 들어, '이 문장을 따라서 간단한 인사말을 해보세요: \"Good morning\" 이라는 단어를 따라해보세요.'"
        f"라는 형태로 지금의 {curriculum_title} 에 해당하는 분야의 대화를 통해 학생의 영어 실력을 향상시키는 것이 목표입니다."
    )

# LLM 체인 생성
def create_chain(grade, curriculum_title):
    """대화 체인 생성"""
    # 시스템 프롬프트 템플릿
    system_prompt = create_system_prompt(grade, curriculum_title)
    
    # 채팅 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    # 디버깅을 위한 콜백 핸들러
    handler = StdOutCallbackHandler()
    callback_manager = CallbackManager([handler])

    # LLM 설정 (콜백 매니저 추가)
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        api_key=openai_api_key,
        callback_manager=callback_manager,
        verbose=True  # 자세한 로깅 활성화
    )
    
    # 순차 실행 체인 생성
    chain = prompt | llm
    
    return chain

@app.route('/')
def home():
    # 사용자 세션 ID가 없으면 생성
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('home.html', grades=curriculums.keys())

@app.route('/grade/<int:grade>')
def grade(grade):
    # 사용자 세션 ID가 없으면 생성
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        
    if grade in curriculums:
        curriculums_with_index = list(enumerate(curriculums[grade]))
        return render_template('grade.html', grade=grade, curriculums=curriculums_with_index, grades=curriculums.keys())
    return "해당 학년은 존재하지 않습니다.", 404

@app.route('/grade/<int:grade>/curriculum/<int:curriculum_id>', methods=['GET', 'POST'])
def curriculum(grade, curriculum_id):
    # 사용자 세션 ID가 없으면 생성
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    if grade in curriculums and 0 <= curriculum_id < len(curriculums[grade]):
        curriculum_title = curriculums[grade][curriculum_id]
        
        if request.method == 'POST':
            user_input = request.form['user_input']
            history_id = f"{user_id}_{grade}_{curriculum_title}"

            # 사용자 입력 로깅
            logger.info(f"\n> 학생 입력: {user_input}")
            
            # 체인 생성
            chain = create_chain(grade, curriculum_title)
            
            # 히스토리와 함께 실행 가능한 체인 생성
            chain_with_history = RunnableWithMessageHistory(
                chain,
                lambda session_id: get_chat_history(user_id, grade, curriculum_title),
                input_messages_key="input",
                history_messages_key="history",
            )
            
            # 대화 기록 출력 (요청 처리 전)
            logger.info("\n> 요청 처리 전 대화 기록:")
            print_chat_history(history_id)
            
            # 응답 생성
            response = chain_with_history.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": history_id}}
            )
            
            # 응답에서 내용 추출
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # 응답 로깅
            logger.info(f"\n> AI 응답: {response_content}")
            
            # 대화 기록 출력 (요청 처리 후)
            logger.info("\n> 요청 처리 후 대화 기록:")
            print_chat_history(history_id)
            
            return jsonify({'response': response_content})
        
        return render_template('curriculum.html', grade=grade, curriculum_title=curriculum_title, grades=curriculums.keys())
    
    return "해당 커리큘럼은 존재하지 않습니다.", 404

# 대화 기록 조회 API 추가
@app.route('/history/<int:grade>/curriculum/<int:curriculum_id>', methods=['GET'])
def view_history(grade, curriculum_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '세션이 없습니다.'}), 400
        
    user_id = session['user_id']
    
    if grade in curriculums and 0 <= curriculum_id < len(curriculums[grade]):
        curriculum_title = curriculums[grade][curriculum_id]
        history_id = f"{user_id}_{grade}_{curriculum_title}"
        
        if history_id in chat_histories:
            history = chat_histories[history_id]
            # 메시지를 읽기 쉬운 형식으로 변환
            formatted_messages = []
            for msg in history.messages:
                role = "system" if isinstance(msg, SystemMessage) else "user" if isinstance(msg, HumanMessage) else "assistant"
                formatted_messages.append({"role": role, "content": msg.content})
            
            return jsonify({
                'status': 'success', 
                'history': formatted_messages,
                'count': len(formatted_messages)
            })
    
    return jsonify({'status': 'error', 'message': '대화 기록을 찾을 수 없습니다.'}), 404

# 대화 초기화를 위한 엔드포인트
@app.route('/reset/<int:grade>/curriculum/<int:curriculum_id>', methods=['POST'])
def reset_conversation(grade, curriculum_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '세션이 없습니다.'}), 400
        
    user_id = session['user_id']
    
    if grade in curriculums and 0 <= curriculum_id < len(curriculums[grade]):
        curriculum_title = curriculums[grade][curriculum_id]
        history_id = f"{user_id}_{grade}_{curriculum_title}"
        
        if history_id in chat_histories:
            # 채팅 기록 초기화 전 로깅
            logger.info(f"\n> 대화 초기화 전 ({history_id}):")
            print_chat_history(history_id)
            
            # 채팅 기록 초기화
            chat_histories[history_id] = ChatMessageHistory()
            
            logger.info(f"\n> 대화 초기화 완료 ({history_id})")
            
            return jsonify({'status': 'success', 'message': '대화가 초기화되었습니다.'})
    
    return jsonify({'status': 'error', 'message': '대화 초기화에 실패했습니다.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
