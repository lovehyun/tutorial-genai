from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw
import requests
import os

# Load environment variables
load_dotenv(dotenv_path='../../.env')

# Instantiate the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Convert the image to RGBA format
with Image.open("DATA/generated_image.png") as img:
    rgba_img = img.convert("RGBA")
    rgba_img.save("DATA/generated_image_rgba.png")

# Create a mask image
with Image.open("DATA/generated_image_rgba.png") as base_img:
    width, height = base_img.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    edit_area = (width//4, height//4, 3*width//4, 3*height//4)
    draw.rectangle(edit_area, fill=255)
    mask.save("DATA/mask.png")

# Perform the image edit request
response = client.images.edit(
    image=open("DATA/generated_image_rgba.png", "rb"),
    mask=open("DATA/mask.png", "rb"),
    prompt="A cute baby sea otter wearing a beret",
    n=2,
    size="1024x1024",
    response_format="url"
)

# Extract and save the generated images
for idx, data in enumerate(response.data):
    image_url = data.url
    print(image_url)

    # Download and save the image
    image_response = requests.get(image_url)
    with open(f"DATA/generated_image2_{idx}.png", "wb") as file:
        file.write(image_response.content)
