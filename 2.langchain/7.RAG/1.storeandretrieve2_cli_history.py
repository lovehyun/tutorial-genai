from dotenv import load_dotenv
import json
import os
from datetime import datetime
import glob

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory

# 환경 변수 로드
load_dotenv()

class ChatSessionManager:
    def __init__(self, sessions_dir="chat_sessions"):
        self.sessions_dir = sessions_dir
        self.ensure_sessions_directory()
        
        # LLM 설정
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
        # 프롬프트 설정
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""당신은 친근하고 도움이 되는 한국어 AI 어시스턴트입니다. 
            이전 대화 내용을 참고해서 자연스럽고 일관성 있는 대화를 이어가세요."""),
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content="{input}")
        ])
        
        # 체인 구성
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def ensure_sessions_directory(self):
        """세션 디렉토리 생성"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
    
    def generate_session_filename(self, session_name):
        """세션 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in session_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{timestamp}_{safe_name}.json"
    
    def save_session(self, history, session_name):
        """세션 저장"""
        filename = self.generate_session_filename(session_name)
        filepath = os.path.join(self.sessions_dir, filename)
        
        session_data = {
            "session_name": session_name,
            "created_at": datetime.now().isoformat(),
            "message_count": len(history.messages),
            "messages": []
        }
        
        for msg in history.messages:
            session_data["messages"].append({
                "type": msg.type,
                "content": msg.content
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print(f"세션이 저장되었습니다: {filename}")
        return filename
    
    def list_sessions(self):
        """저장된 세션 목록 조회"""
        session_files = glob.glob(os.path.join(self.sessions_dir, "*.json"))
        sessions = []
        
        for filepath in session_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "filename": os.path.basename(filepath),
                        "session_name": data.get("session_name", "Unknown"),
                        "created_at": data.get("created_at", "Unknown"),
                        "message_count": data.get("message_count", 0)
                    })
            except Exception as e:
                print(f"세션 파일 읽기 오류 {filepath}: {e}")
                continue
        
        # 생성 시간순 정렬
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions
    
    def load_session(self, filename):
        """세션 로드"""
        filepath = os.path.join(self.sessions_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"세션 파일을 찾을 수 없습니다: {filename}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history = ChatMessageHistory()
            for msg_data in data["messages"]:
                if msg_data["type"] == "human":
                    history.add_user_message(msg_data["content"])
                elif msg_data["type"] == "ai":
                    history.add_ai_message(msg_data["content"])
            
            print(f"세션을 불러왔습니다: {data.get('session_name', 'Unknown')}")
            print(f"메시지 수: {len(history.messages)}")
            return history
            
        except Exception as e:
            print(f"세션 로드 중 오류 발생: {e}")
            return None
    
    def show_session_list(self):
        """세션 목록 출력"""
        sessions = self.list_sessions()
        
        if not sessions:
            print("저장된 세션이 없습니다.")
            return sessions
        
        print("\n=== 저장된 세션 목록 ===")
        for i, session in enumerate(sessions, 1):
            created = session["created_at"][:19].replace("T", " ")  # 날짜 포맷
            print(f"{i:2d}. {session['session_name']} ({session['message_count']}개 메시지)")
            print(f"    파일: {session['filename']}")
            print(f"    생성: {created}")
            print()
        
        return sessions
    
    def chat_with_history(self, history, user_input):
        """대화 처리"""
        try:
            response = self.chain.invoke({
                "history": history.messages,
                "input": user_input
            })
            
            # 대화 기록 업데이트
            history.add_user_message(user_input)
            history.add_ai_message(response)
            
            return response
        except Exception as e:
            print(f"AI 응답 생성 중 오류 발생: {e}")
            return None
    
    def print_recent_history(self, history, last_n=5):
        """최근 대화 내역 출력"""
        if not history.messages:
            print("대화 내역이 없습니다.")
            return
        
        messages = history.messages[-last_n*2:]  # 최근 N개 대화 (사용자+AI 쌍)
        
        print(f"\n=== 최근 {min(last_n, len(messages)//2)} 대화 ===")
        for msg in messages:
            role = "사용자" if msg.type == "human" else "AI"
            print(f"{role}: {msg.content}")
        print()
    
    def start_new_session(self):
        """새 세션 시작"""
        session_name = input("새 세션 이름을 입력하세요: ").strip()
        if not session_name:
            session_name = f"세션_{datetime.now().strftime('%m%d_%H%M')}"
        
        history = ChatMessageHistory()
        self.run_chat_session(history, session_name)
    
    def load_existing_session(self):
        """기존 세션 로드"""
        sessions = self.show_session_list()
        
        if not sessions:
            return
        
        try:
            choice = input("불러올 세션 번호를 입력하세요: ").strip()
            session_idx = int(choice) - 1
            
            if 0 <= session_idx < len(sessions):
                selected_session = sessions[session_idx]
                history = self.load_session(selected_session["filename"])
                
                if history:
                    self.print_recent_history(history, 3)
                    self.run_chat_session(history, selected_session["session_name"])
            else:
                print("잘못된 번호입니다.")
                
        except ValueError:
            print("올바른 번호를 입력해주세요.")
    
    def run_chat_session(self, history, session_name):
        """채팅 세션 실행"""
        print(f"\n=== '{session_name}' 세션 ===")
        print("명령어: 'save' (저장), 'history' (대화내역), 'quit' (종료)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n사용자: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    # 종료 시 자동 저장 여부 확인
                    save_choice = input("종료 전에 세션을 저장하시겠습니까? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        self.save_session(history, session_name)
                    print("대화를 종료합니다.")
                    break
                
                elif user_input.lower() == 'save':
                    self.save_session(history, session_name)
                    continue
                
                elif user_input.lower() == 'history':
                    self.print_recent_history(history, 10)
                    continue
                
                # AI 응답 생성
                print("AI 응답 생성 중...")
                response = self.chat_with_history(history, user_input)
                
                if response:
                    print(f"AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n대화가 중단되었습니다.")
                break
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")
    
    def run(self):
        """메인 실행"""
        print("한글 대화 세션 관리 시스템")
        
        while True:
            print("\n" + "="*40)
            print("1. 새 세션 시작")
            print("2. 기존 세션 불러오기")
            print("3. 세션 목록 보기")
            print("4. 종료")
            
            choice = input("\n선택하세요 (1-4): ").strip()
            
            if choice == "1":
                self.start_new_session()
            elif choice == "2":
                self.load_existing_session()
            elif choice == "3":
                self.show_session_list()
            elif choice == "4":
                print("프로그램을 종료합니다.")
                break
            else:
                print("올바른 번호를 입력해주세요.")

# 실행
if __name__ == "__main__":
    manager = ChatSessionManager()
    manager.run()
