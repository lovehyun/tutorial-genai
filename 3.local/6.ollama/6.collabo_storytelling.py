import ollama

def continue_story(story):
    prompt = f"다음 문장을 이어서 작성해 주세요. 현재 이야기:\n{story}\n\n다음 문장:"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

story = "옛날 옛적, 깊은 숲속에 마법사가 살고 있었습니다."
while True:
    print(f"\n이야기: {story}\n")
    user_input = input("당신이 이어서 쓸 문장: ")
    story += " " + user_input
    ai_story = continue_story(story)
    story += " " + ai_story
    print(f"AI: {ai_story}")
