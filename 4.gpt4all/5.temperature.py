# Modify the temperature setting to control response creativity.
# A higher temperature value results in more creative responses.

from gpt4all import GPT4All

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Start a chat session
with model.chat_session() as session:
    # Generate a response with a specified temperature
    response = session.generate("Tell me a joke.", max_tokens=50, temp=0.7)
    print(response)
