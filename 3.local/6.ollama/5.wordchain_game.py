import ollama

def get_next_word(previous_word):
    """AI가 끝말잇기 규칙을 따르도록 다음 단어를 생성"""
    prompt = f"끝말잇기 게임 중입니다. '{previous_word[-1]}'(으)로 시작하는 단어를 한 단어만 설명 없이 말해주세요."
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# 사용자가 직접 첫 단어 입력
user_input = input("게임을 시작할 단어를 입력하세요: ").strip()

while True:
    print(f"사용자: {user_input}")
    
    # AI가 끝말잇기 단어 생성
    ai_word = get_next_word(user_input)
    print(f"AI: {ai_word}")
    
    # 사용자 입력
    user_input = input("당신의 단어: ").strip()
