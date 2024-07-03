from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with model.chat_session() as session:
    response = session.generate("Hi, how are you?")
    print(response)
    response = session.generate("What's the weather like today?", max_tokens=50)
    # response = session.generate("What's the weather like today?", max_tokens=150)
    print(response)
