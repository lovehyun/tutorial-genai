from gpt4all import GPT4All

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Read content from the documents
with open("document1.txt", "r") as file:
    doc1_content = file.read()

with open("document2.txt", "r") as file:
    doc2_content = file.read()

# Combine the content for summarization
combined_content = f"Document 1:\n{doc1_content}\n\nDocument 2:\n{doc2_content}"

# Start a chat session
with model.chat_session() as session:
    # Generate a summary
    prompt = f"Summarize the main points from the following documents:\n{combined_content}"
    response = session.generate(prompt, max_tokens=200)
    print(response)
