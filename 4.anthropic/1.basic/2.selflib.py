import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

class PromptTemplate:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-7-sonnet-20250219"
    
    def basic_response(self, query, max_tokens=1000):
        """기본 응답 생성"""
        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": query}]
        )
    
    def expert_response(self, query, expertise, max_tokens=1000):
        """전문가 스타일 응답"""
        prompt = f"당신은 {expertise} 분야의 전문가입니다. 다음 질문에 전문적으로 답변해주세요: {query}"
        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
    
    def structured_response(self, query, format_type="json", max_tokens=1000):
        """구조화된 응답 생성"""
        if format_type.lower() == "json":
            prompt = f"""
            다음 질문에 대한 답변을 JSON 형식으로 제공해주세요:
            
            질문: {query}
            
            JSON 형식으로만 응답해주세요. 설명은 포함하지 마세요.
            """
        elif format_type.lower() == "bullet":
            prompt = f"""
            다음 질문에 대한 답변을 불릿 포인트로 제공해주세요:
            
            질문: {query}
            
            각 항목을 '- ' 형식으로 시작하는 불릿 포인트로 나열해주세요.
            """
        else:
            prompt = query
            
        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

# 사용 예시
if __name__ == "__main__":
    template = PromptTemplate()
    
    # 기본 응답
    basic_response = template.basic_response("인공지능의 미래 전망은 어떤가요?")
    print("기본 응답:")
    print(basic_response.content[0].text[:200] + "...\n")
    
    # 전문가 응답
    expert_response = template.expert_response("인공지능의 미래 전망은 어떤가요?", "AI 연구")
    print("전문가 응답:")
    print(expert_response.content[0].text[:200] + "...\n")
    
    # 구조화된 응답 (JSON)
    json_response = template.structured_response("세계 3대 AI 기업과 그들의 주요 제품을 알려주세요", "json")
    print("JSON 응답:")
    print(json_response.content[0].text[:200] + "...\n")
    
    # 구조화된 응답 (불릿)
    bullet_response = template.structured_response("건강한 생활 습관 5가지를 알려주세요", "bullet")
    print("불릿 포인트 응답:")
    print(bullet_response.content[0].text[:200] + "...")
