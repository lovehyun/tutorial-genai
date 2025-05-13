import requests
from openai import OpenAI
from PIL import Image
from io import BytesIO
from flask import Flask, request, render_template, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import uuid
import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    # Get all images from the gallery
    gallery_images = get_gallery_images()
    return render_template('index.html', gallery_images=gallery_images)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    print(f"Generate prompt: {prompt}")
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"image_{timestamp}_{unique_id}.png"
        
        # Ensure directories exist
        os.makedirs('static/gallery', exist_ok=True)
        os.makedirs('static/thumbnails', exist_ok=True)
        
        # Save original image
        img.save(f'static/gallery/{filename}')
        
        # Create and save thumbnail
        thumbnail_size = (300, 300)
        img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        img.save(f'static/thumbnails/{filename}')
        
        # Create metadata for the image
        save_image_metadata(filename, prompt)
        
        # Get updated gallery images
        gallery_images = get_gallery_images()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'gallery_images': gallery_images
        })
    
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def save_image_metadata(filename, prompt):
    """Save image metadata to a JSON file"""
    import json
    
    metadata_file = 'static/metadata.json'
    
    # Load existing metadata if it exists
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Add new image metadata
    timestamp = datetime.datetime.now().isoformat()
    metadata[filename] = {
        'prompt': prompt,
        'created_at': timestamp
    }
    
    # Save metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def get_gallery_images():
    """Get all images from the gallery with their metadata"""
    import json
    
    metadata_file = 'static/metadata.json'
    
    # Load metadata if it exists
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Get all image files from gallery
    gallery_dir = 'static/gallery'
    if not os.path.exists(gallery_dir):
        return []
    
    image_files = [f for f in os.listdir(gallery_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    gallery_images = []
    for image_file in image_files:
        image_data = {
            'filename': image_file,
            'thumbnail': f'/static/thumbnails/{image_file}',
            'fullsize': f'/static/gallery/{image_file}',
            'prompt': 'Unknown prompt',
            'created_at': ''
        }
        
        # Add metadata if available
        if image_file in metadata:
            image_data['prompt'] = metadata[image_file]['prompt']
            image_data['created_at'] = metadata[image_file]['created_at']
        
        gallery_images.append(image_data)
    
    # Sort by created_at (newest first)
    gallery_images.sort(key=lambda x: x['created_at'], reverse=True)
    
    return gallery_images

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/gallery', filename)

if __name__ == '__main__':
    app.run(debug=True)