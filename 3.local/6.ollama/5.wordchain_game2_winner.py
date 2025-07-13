import ollama
import re

# AI 응답에서 괄호 안의 설명이나 여러 단어 제거
def clean_word(word):
    """AI가 반환한 단어에서 불필요한 설명(괄호 포함)이나 공백을 제거"""
    word = word.split()[0]  # 첫 번째 단어만 사용
    word = re.sub(r"\(.*?\)", "", word)  # 괄호 안의 내용을 제거
    return word.strip().lower()

# 끝말잇기 유효성 검사 함수
def is_valid_word(previous_word, new_word, used_words):
    """끝말잇기 규칙 검사: 이전 단어의 마지막 글자로 시작해야 하며, 중복 단어 사용 금지"""
    new_word = clean_word(new_word)  # AI가 반환한 단어에서 불필요한 설명 제거

    if not new_word:
        return "빈 단어는 사용할 수 없습니다."
    
    if previous_word[-1] != new_word[0]:  # 끝말잇기 규칙 위반
        return f"'{new_word}'는 '{previous_word[-1]}'로 시작해야 합니다."

    if new_word in used_words:  # 끝말잇기 규칙 위반
        return f"'{new_word}'는 이미 사용된 단어입니다."
        
    return None  # 유효한 단어

# AI가 끝말잇기 단어 생성 (불필요한 설명 제거)
def get_next_word(previous_word, used_words):
    """AI가 끝말잇기 규칙을 따르도록 다음 단어를 생성"""
    prompt = (
        f"끝말잇기 게임 중입니다. '{previous_word[-1]}'(으)로 시작하는 단어를 하나만 말하세요. "
        f"지금까지 사용한 단어는 {', '.join(used_words)}입니다. "
        f"이미 사용한 단어는 말하면 안 됩니다. 오직 한 단어만 말하세요."
    )
    
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return clean_word(response["message"]["content"].strip().lower())

# 사용자 첫 단어 입력
user_input = input("게임을 시작할 단어를 입력하세요: ").strip().lower()
used_words = {user_input}  # 사용한 단어 저장 (집합 사용으로 빠른 검색)

while True:
    print(f"사용자: {user_input}")
    
    # AI가 끝말잇기 단어 생성
    ai_word = get_next_word(user_input, used_words)
    print(f"AI: {ai_word}")
    
    # AI가 끝말잇기 규칙 위반했는지 검사
    error_message = is_valid_word(user_input, ai_word, used_words)
    if error_message:
        print(f"❌ AI가 틀렸습니다! {error_message}")
        print("🎉 Winner: 사용자! 🎉")
        break
    
    used_words.add(ai_word)  # AI 단어 추가
    
    # 사용자 입력
    user_input = input("당신의 단어: ").strip().lower()
    
    # 사용자가 끝말잇기 규칙 위반했는지 검사
    error_message = is_valid_word(ai_word, user_input, used_words)
    if error_message:
        print(f"❌ 사용자가 틀렸습니다! {error_message}")
        print("🤖 Winner: AI! 🤖")
        break
    
    used_words.add(user_input)  # 사용자 단어 추가
