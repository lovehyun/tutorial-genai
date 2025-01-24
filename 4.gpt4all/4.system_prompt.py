from gpt4all import GPT4All

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Start a chat session with a custom system prompt
with model.chat_session(system_prompt="You are a helpful assistant.") as session:
    response = session.generate("Give me a tip for staying productive.", max_tokens=50)
    print(response)
