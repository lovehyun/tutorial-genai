from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain.chains import ConversationChain

load_dotenv()

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

conversation = ConversationChain(llm=llm, verbose=False)

print("Welcome to your AI Chatbot! What's on your mind?")
for _ in range(0, 3):
    human_input = input("You: ")
    ai_response = conversation.predict(input=human_input)
    print(f"AI: {ai_response}")
