import os
import anthropic
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

class ConversationManager:
    def __init__(self, model="claude-3-7-sonnet-20250219", max_tokens=1000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.conversations = {}
    
    def create_conversation(self, conversation_id=None):
        """새 대화 생성"""
        if conversation_id is None:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        return conversation_id
    
    def add_message(self, conversation_id, role, content):
        """대화에 메시지 추가"""
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation(conversation_id)
        
        message = {"role": role, "content": content}
        self.conversations[conversation_id]["messages"].append(message)
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
        
        return message
    
    def get_messages(self, conversation_id):
        """대화의 모든 메시지 가져오기"""
        if conversation_id not in self.conversations:
            return []
        
        return self.conversations[conversation_id]["messages"]
    
    def send_message(self, conversation_id, user_message, system_prompt=None):
        """대화에 메시지 추가 및 응답 받기"""
        # 사용자 메시지 추가
        self.add_message(conversation_id, "user", user_message)
        
        # API 요청용 메시지 준비
        api_messages = []
        
        # 시스템 프롬프트가 있으면 추가
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        
        # 이전 대화 내용 추가
        api_messages.extend(self.get_messages(conversation_id))
        
        # API 호출
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=api_messages
        )
        
        # 응답 메시지 추가
        assistant_message = response.content[0].text
        self.add_message(conversation_id, "assistant", assistant_message)
        
        return assistant_message
    
    def get_conversation_history(self, conversation_id):
        """대화 이력 가져오기"""
        if conversation_id not in self.conversations:
            return None
        
        return self.conversations[conversation_id]
    
    def save_conversation(self, conversation_id, file_path=None):
        """대화를 파일로 저장"""
        if conversation_id not in self.conversations:
            return False
        
        if file_path is None:
            file_path = f"{conversation_id}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.conversations[conversation_id], f, ensure_ascii=False, indent=2)
        
        return True
    
    def load_conversation(self, file_path):
        """파일에서 대화 불러오기"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                conversation_data = json.load(f)
            
            conversation_id = os.path.splitext(os.path.basename(file_path))[0]
            self.conversations[conversation_id] = conversation_data
            
            return conversation_id
        except Exception as e:
            print(f"대화 불러오기 실패: {e}")
            return None
    
    def delete_conversation(self, conversation_id):
        """대화 삭제"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

# 사용 예시
if __name__ == "__main__":
    conv_manager = ConversationManager()
    
    # 새 대화 생성
    conv_id = conv_manager.create_conversation()
    print(f"새 대화 ID: {conv_id}")
    
    # 첫 번째 메시지 보내기
    response = conv_manager.send_message(
        conv_id, 
        "안녕하세요! 인공지능에 대해 알고 싶습니다."
    )
    print(f"Claude 응답: {response[:100]}...\n")
    
    # 후속 질문
    response = conv_manager.send_message(
        conv_id,
        "인공지능의 발전 단계를 간략히 설명해주세요."
    )
    print(f"Claude 응답: {response[:100]}...\n")
    
    # 대화 저장
    conv_manager.save_conversation(conv_id)
    print(f"대화가 {conv_id}.json 파일로 저장되었습니다.")
