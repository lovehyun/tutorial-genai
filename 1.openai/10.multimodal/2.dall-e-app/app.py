# Fixed Python Code (app.py)

import openai
import requests
from PIL import Image, ImageDraw
from io import BytesIO
from flask import Flask, request, render_template, send_from_directory, jsonify
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='../../.env')

# Initialize OpenAI client
client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    print(f"Generate prompt: {prompt}")
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))
    
    # Ensure the directory exists
    os.makedirs('static/img', exist_ok=True)
    img.save('static/img/generated_image.png')
    
    # Also save as uploaded_image for editing
    img.save('static/img/uploaded_image.png')
    
    return send_from_directory('static/img', 'generated_image.png')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Ensure the directory exists
        os.makedirs('static/img', exist_ok=True)
        
        filename = 'uploaded_image.png'
        file.save(f'static/img/{filename}')
        print(f"Uploaded file: {filename}")
        return send_from_directory('static/img', filename)

@app.route('/generate_mask', methods=['POST'])
def generate_mask():
    coordinates = request.json.get('coordinates')
    print(f"Mask coordinates: {coordinates}")
    
    # Open the uploaded image
    image = Image.open('static/img/uploaded_image.png')
    
    # Create a black mask (black = keep, white = edit)
    mask = Image.new("L", image.size, 0)  # Start with all black (keep everything)
    draw = ImageDraw.Draw(mask)
    
    # Draw white rectangles on the mask for the areas to edit
    for coord in coordinates:
        x0, y0 = coord['x'], coord['y']
        x1, y1 = x0 + coord['width'], y0 + coord['height']
        # Handle negative width/height
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        draw.rectangle([x0, y0, x1, y1], fill=255)  # White = areas to edit
    
    # Save the mask
    mask.save('static/img/mask.png')
    
    return jsonify({'message': 'Mask generated successfully', 'mask_path': '/static/img/mask.png'})

@app.route('/edit', methods=['POST'])
def edit():
    prompt = request.form['prompt']
    print(f"Edit prompt: {prompt}")
    
    try:
        # Verify files exist
        with open('static/img/uploaded_image.png', 'rb') as img_file:
            with open('static/img/mask.png', 'rb') as mask_file:
                # Make the edit request to OpenAI
                response = client.images.edit(
                    image=open('static/img/uploaded_image.png', 'rb'),
                    mask=open('static/img/mask.png', 'rb'),
                    prompt=prompt,
                    n=1,
                    size="512x512"
                )
                
                # Get the resulting image
                image_url = response.data[0].url
                image_response = requests.get(image_url)
                img = Image.open(BytesIO(image_response.content))
                img.save('static/img/edited_image.png')
                
                # Update the uploaded image to be the edited image
                # This way, further edits will be applied to the latest version
                img.save('static/img/uploaded_image.png')
                
                return send_from_directory('static/img', 'edited_image.png')
    except Exception as e:
        print(f"Error during edit: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
