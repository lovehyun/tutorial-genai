import os
from multiprocessing import Pool, cpu_count
from gpt4all import GPT4All

# Initialize the model globally
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Function to read the entire content of a document
def read_entire_document(file_path):
    with open(file_path, "r") as file:
        return file.read()

# Function to split document content into chunks
def split_into_chunks(text, chunk_size=2000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Function to summarize a single chunk (this function needs to be defined globally)
def summarize_chunk(chunk_index_pair):
    i, chunk = chunk_index_pair
    with model.chat_session() as session:
        print(f"Processing chunk {i + 1}:\n{chunk[:200]}...")  # Display the first 200 characters of each chunk
        prompt = f"Summarize the following text:\n{chunk}"
        summary = session.generate(prompt, max_tokens=100)  # Adjust max_tokens for summaries
        print(f"Summary {i + 1}:\n{summary}\n")
    return summary

# Function to summarize chunks using multiprocessing
def summarize_chunks_parallel(chunks):
    with Pool(cpu_count()) as pool:
        summaries = pool.map(summarize_chunk, enumerate(chunks))
    return summaries

if __name__ == "__main__":
    # Read entire documents
    doc1_content = read_entire_document("large_document1.txt")
    doc2_content = read_entire_document("large_document2.txt")

    # Split documents into chunks
    chunks1 = split_into_chunks(doc1_content)
    chunks2 = split_into_chunks(doc2_content)

    # Calculate the number of chunks
    num_chunks1 = len(chunks1)
    num_chunks2 = len(chunks2)
    print(f"Document 1 will be split into {num_chunks1} chunks.")
    print(f"Document 2 will be split into {num_chunks2} chunks.")

    # Summarize chunks for document 1 in parallel
    summaries1 = summarize_chunks_parallel(chunks1)
    final_summary1 = " ".join(summaries1)
    print(f"Final summary for document 1:\n{final_summary1}\n")

    # Summarize chunks for document 2 in parallel
    summaries2 = summarize_chunks_parallel(chunks2)
    final_summary2 = " ".join(summaries2)
    print(f"Final summary for document 2:\n{final_summary2}\n")

    # Combine final summaries for a comprehensive summary
    combined_summary_prompt = f"Combine the following summaries into a comprehensive summary:\nSummary 1: {final_summary1}\n\nSummary 2: {final_summary2}"
    with model.chat_session() as session:
        final_combined_summary = session.generate(combined_summary_prompt, max_tokens=200)
        print(f"Final combined summary:\n{final_combined_summary}")
 