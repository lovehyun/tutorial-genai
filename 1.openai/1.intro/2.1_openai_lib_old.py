# pip install python-dotenv openai==0.28

import openai
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')

# Set the OpenAI API key
openai.api_key = openai_api_key

def ask_chatgpt(user_input):
    try:
        # Use the OpenAI library to get a response from the chat model
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': user_input},
            ]
        )
        print('-'*20)
        print('Response JSON:', response)  # Print the entire response for debugging
        print('-'*20)

        return response['choices'][0]['message']['content']
    except Exception as error:
        print('ChatGPT API 요청 중 오류 발생:', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

def chat_with_user():
    user_input = '안녕, 챗봇!'
    # user_input = input("\n당신: ").strip()
    
    chat_gpt_response = ask_chatgpt(user_input)
    print('챗봇 응답:', chat_gpt_response)

if __name__ == "__main__":
    chat_with_user()
