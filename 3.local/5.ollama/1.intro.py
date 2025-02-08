# https://ollama.com/download

# pip install ollama
# ollama pull mistral

import ollama

ollama.pull("mistral")
response = ollama.chat(model="mistral", messages=[{"role": "user", "content": "안녕?"}])
print(response["message"]["content"])
