from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with model.chat_session():
    response = model.generate("What is the capital of France?", max_tokens=20)
    print(response)
