import os
from gpt4all import GPT4All

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Function to read a document in chunks
def read_document_in_chunks(file_path, chunk_size=2000):
    with open(file_path, "r") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Function to summarize chunks
def summarize_chunks(chunks):
    summaries = []
    with model.chat_session() as session:
        for chunk in chunks:
            prompt = f"Summarize the following text:\n{chunk}"
            summary = session.generate(prompt, max_tokens=100)
            summaries.append(summary)
    return summaries

# Read and summarize large document 1
chunks1 = read_document_in_chunks("large_document1.txt")
summaries1 = summarize_chunks(chunks1)
final_summary1 = " ".join(summaries1)

# Read and summarize large document 2
chunks2 = read_document_in_chunks("large_document2.txt")
summaries2 = summarize_chunks(chunks2)
final_summary2 = " ".join(summaries2)

# Combine final summaries for a comprehensive summary
combined_summary_prompt = f"Combine the following summaries into a comprehensive summary:\nSummary 1: {final_summary1}\n\nSummary 2: {final_summary2}"
with model.chat_session() as session:
    final_combined_summary = session.generate(combined_summary_prompt, max_tokens=200)
    print(final_combined_summary)
