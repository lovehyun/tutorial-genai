import time
from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with model.chat_session() as session:
    response = session.generate("Explain the theory of relativity.", max_tokens=500)
    for i in range(0, len(response), 100):
        print(response[i:i+100])  # Print 100 characters at a time
        time.sleep(0.5)  # Wait for 0.5 seconds before printing the next chunk
