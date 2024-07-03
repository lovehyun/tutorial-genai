from gpt4all import GPT4All

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Define prompts
prompt1 = "Provide an overview of World War II."

prompt2 = """
You are a knowledgeable historian. Provide a detailed overview of the causes and effects of World War II.
"""

prompt3_regular = """
Provide a comprehensive analysis of the causes and effects of World War II. Focus on:
1. The economic and political conditions in Europe after World War I that led to the rise of totalitarian regimes.
2. The major alliances and political strategies leading up to the war.
3. Key battles and turning points during the war.
4. The immediate and long-term effects on global geopolitics, including the establishment of the United Nations and the onset of the Cold War.
Provide detailed insights and analyses for each of these points.
"""

system_prompt3 = "You are a highly knowledgeable historian and expert in 20th-century conflicts."

prompt4_part1 = """
Provide a comprehensive analysis of the economic and political conditions in Europe after World War I that led to the rise of totalitarian regimes.
"""
prompt4_part2 = """
Discuss the major alliances and political strategies leading up to World War II.
"""
prompt4_part3 = """
Describe key battles and turning points during World War II.
"""
prompt4_part4 = """
Analyze the immediate and long-term effects on global geopolitics, including the establishment of the United Nations and the onset of the Cold War.
"""

# Run the chat session and generate responses
with model.chat_session() as session:
    response1 = session.generate(prompt1, max_tokens=500)
    print("Prompt 1 Response:\n" + "="*50 + "\n" + response1 + "\n" + "="*50 + "\n")

    response2 = session.generate(prompt2, max_tokens=500)
    print("Prompt 2 Response:\n" + "="*50 + "\n" + response2 + "\n" + "="*50 + "\n")

    # Third prompt with regular prompt
    response3_regular = session.generate(prompt3_regular, max_tokens=500)
    print("Prompt 3 Regular Response:\n" + "="*50 + "\n" + response3_regular + "\n" + "="*50 + "\n")

# Run the chat session with a system prompt for the third prompt
with model.chat_session(system_prompt=system_prompt3) as session:
    response3_system = session.generate(prompt3_regular, max_tokens=500)
    print("Prompt 3 System Prompt Response:\n" + "="*50 + "\n" + response3_system + "\n" + "="*50 + "\n")

# Run the chat session for the fourth, detailed, broken-down prompt
with model.chat_session() as session:
    response4_part1 = session.generate(prompt4_part1, max_tokens=500)
    print("Prompt 4 Part 1 Response:\n" + "="*50 + "\n" + response4_part1 + "\n" + "="*50 + "\n")

    response4_part2 = session.generate(prompt4_part2, max_tokens=500)
    print("Prompt 4 Part 2 Response:\n" + "="*50 + "\n" + response4_part2 + "\n" + "="*50 + "\n")

    response4_part3 = session.generate(prompt4_part3, max_tokens=500)
    print("Prompt 4 Part 3 Response:\n" + "="*50 + "\n" + response4_part3 + "\n" + "="*50 + "\n")

    response4_part4 = session.generate(prompt4_part4, max_tokens=500)
    print("Prompt 4 Part 4 Response:\n" + "="*50 + "\n" + response4_part4 + "\n" + "="*50 + "\n")
