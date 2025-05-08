import openai
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='../../.env')

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_image(prompt, model, filename):
    # Request image generation from OpenAI's DALL-E model
    response = client.images.generate(
        prompt=prompt,
        n=1,  # Number of images to generate
        size="1024x1024",  # Image size
        model=model  # Model to use (e.g., "dall-e-2" or "dall-e-3")
    )

    # Get the URL of the generated image
    image_url = response.data[0].url

    # Download the image from the URL
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))

    # Display the image
    # img.show()

    # Save the image to a file
    img.save(f"DATA/{filename}")

# Set the prompt
prompt = "A futuristic cityscape with flying cars"

# Generate and save image using DALL-E 2
generate_image(prompt, "dall-e-2", "generated_image_dalle2.png")

# Generate and save image using DALL-E 3
generate_image(prompt, "dall-e-3", "generated_image_dalle3.png")
