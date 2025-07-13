import ollama

def continue_story(story):
    """AI가 현재 이야기를 기반으로 다음 문장을 이어서 작성"""
    prompt = f"다음 문장을 이어서 작성해 주세요. 현재 이야기:\n{story}\n\n다음 문장:"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# 이야기 시작
story = "옛날 옛적, 깊은 숲속에 마법사가 살고 있었습니다."

while True:
    print(f"\n이야기: {story}\n")
    
    # 사용자 입력
    user_input = input("당신이 이어서 쓸 문장 ('끝'을 입력하면 종료): ").strip()
    
    # 사용자가 "끝" 입력 시 종료 및 전체 이야기 출력
    if user_input == "끝":
        print("\n🎉 최종 이야기 🎉\n")
        print(story)
        break

    # 사용자 입력을 이야기(story)에 추가
    story += " " + user_input
    
    # AI가 이어서 이야기 생성
    ai_story = continue_story(story)
    story += " " + ai_story  # AI 생성 문장 추가

    print(f"AI: {ai_story}")
