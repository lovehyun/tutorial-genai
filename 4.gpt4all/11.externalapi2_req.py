import requests
from gpt4all import GPT4All

# Fetch data from JSONPlaceholder API
api_url = "https://jsonplaceholder.typicode.com/users"
users_data = requests.get(api_url).json()

# Create a summary of the user data
users_info = "\n".join([f"Name: {user['name']}, Email: {user['email']}" for user in users_data])

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Print intermediate result (user information)
print("User Information:\n" + "="*50 + "\n" + users_info + "\n" + "="*50 + "\n")

# Use GPT4All to generate a response based on the API data
with model.chat_session() as session:
    prompt = f"Based on the following user information, provide a suggestion for an email campaign:\n{users_info}"
    response = session.generate(prompt, max_tokens=200)
    
    # Print the final summarized result
    print("Generated Email Campaign Suggestion:\n" + "="*50 + "\n" + response + "\n" + "="*50 + "\n")
