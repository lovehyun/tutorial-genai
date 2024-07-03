from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with open("/path/to/file.txt", "r") as file:
    content = file.read()

with model.chat_session() as session:
    response = session.generate(f"Analyze the following text:\n{content}", max_tokens=500)
    print(response)
