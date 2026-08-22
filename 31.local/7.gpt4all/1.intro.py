from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with model.chat_session():
    print(model.generate("Hello, world!", max_tokens=20))
