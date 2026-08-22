import requests
from gpt4all import GPT4All

# Fetch real-time data from an API
api_url = "http://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q=London"
weather_data = requests.get(api_url).json()
weather_info = f"The current temperature in Seoul is {weather_data['current']['temp_c']}°C."

# Use GPT4All to generate a response based on the API data
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
with model.chat_session() as session:
    response = session.generate(f"Based on the following information, what should I wear today?\n{weather_info}", max_tokens=100)
    print(response)
