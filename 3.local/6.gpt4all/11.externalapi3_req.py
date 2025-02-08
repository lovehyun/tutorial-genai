# pip install yfinance googletrans 
# pip install deep-translator
import os
import requests
import torch
from dotenv import load_dotenv
from datetime import datetime, timedelta
import yfinance as yf
from gpt4all import GPT4All
from googletrans import Translator
from deep_translator import GoogleTranslator


# Load environment variables from .env file
load_dotenv()

# Fetch the API token from environment variables
api_token = os.getenv("STOCKDATA_API_TOKEN")

# Define the function to get historical data for the last 10 trading days
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)  # 14 calendar days to cover 10 trading days
    hist = stock.history(start=start_date, end=end_date)
    return hist

def get_latest_exchange_rate():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            rate = data['rates']['KRW']
            return rate
        except KeyError:
            return "Data not available"
    else:
        return "Failed to retrieve data"

# Fetch historical stock data for AAPL
stock_data = get_stock_data("AAPL")
stock_data_str = "\n".join([f"{index.date()}: ${row['Close']}" for index, row in stock_data.iterrows()])

# Fetch the latest exchange rate data
exchange_rate = get_latest_exchange_rate()
exchange_rate_data_str = f"Latest USD to KRW Exchange Rate: {exchange_rate:.2f} KRW/USD"

# Combine stock and exchange rate information
combined_info = f"Stock Data for AAPL over the last 10 trading days:\n{stock_data_str}\n\n{exchange_rate_data_str}"

# Initialize the model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# System prompt
system_prompt = "You are an expert in stock analysis and investment strategies."

# Print intermediate result (combined data)
print("Combined Stock and Exchange Rate Information:\n" + "="*50 + "\n" + combined_info + "\n" + "="*50 + "\n")

# Use GPT-4All to generate a response based on the combined data
with model.chat_session(system_prompt=system_prompt) as session:
    prompt = (f"I have 1,000,000 KRW in assets. Based on the following stock and exchange rate information, "
              f"how much should I convert to USD and invest in Apple Inc. (AAPL) stock? Consider the current stock price trend and exchange rate. "
            #   f"Provide the answer in English, including:\n"
              f"Provide the answer in both English and Korean, including:\n"
              f"1. The percentage of the total investment and the rationale behind the suggested investment percentage.\n"
              f"2. The amount in KRW to be invested and the equivalent amount in USD.\n"
              f"3. The number of AAPL shares that can be purchased.\n\n{combined_info}")
    response = session.generate(prompt, max_tokens=500)
    
    # Translate the response to Korean
    # translator = Translator()
    # translated_response = translator.translate(response, src='en', dest='ko').text

    # Translate the response to Korean using an alternative translation library
    translator = GoogleTranslator(source='en', target='ko')
    translated_response = translator.translate(response)
    
    # Print the final summarized result in English and Korean
    print("Generated Investment Strategy (English):\n" + "="*50 + "\n" + response + "\n" + "="*50 + "\n")
    print("Generated Investment Strategy (Korean):\n" + "="*50 + "\n" + translated_response + "\n" + "="*50 + "\n")
