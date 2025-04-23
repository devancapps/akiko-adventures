#!/usr/bin/env python3
import os
import requests
from PIL import Image
from io import BytesIO
import sys

def fetch_unsplash_image(query, api_key):
    """Fetch an image from Unsplash API."""
    headers = {
        'Authorization': f'Client-ID {api_key}'
    }
    
    # Search for photos
    search_url = 'https://api.unsplash.com/search/photos'
    params = {
        'query': query,
        'orientation': 'landscape',
        'per_page': 1
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image: {response.status_code}")
    
    data = response.json()
    if not data['results']:
        raise Exception(f"No images found for query: {query}")
    
    # Get the first image URL
    image_url = data['results'][0]['urls']['raw']
    
    # Download the image
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        raise Exception("Failed to download image")
    
    return BytesIO(image_response.content)

def process_image(image_data, output_path, target_size=(1200, 675)):
    """Process the image to the required dimensions."""
    # Open the image
    img = Image.open(image_data)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calculate aspect ratio
    aspect_ratio = target_size[0] / target_size[1]
    
    # Get current dimensions
    width, height = img.size
    current_ratio = width / height
    
    # Calculate dimensions for cropping
    if current_ratio > aspect_ratio:
        # Image is too wide
        new_width = int(height * aspect_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        # Image is too tall
        new_height = int(width / aspect_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))
    
    # Resize to target size
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Save the processed image
    img.save(output_path, 'JPEG', quality=85)

def main(slug, city):
    """Main function to fetch and process an image."""
    api_key = os.getenv('UNSPLASH_API_KEY')
    if not api_key:
        raise Exception("UNSPLASH_API_KEY environment variable not set")
    
    # Create assets directory if it doesn't exist
    assets_dir = 'assets'
    os.makedirs(assets_dir, exist_ok=True)
    
    # Construct the output path
    output_path = os.path.join(assets_dir, f"{slug}.jpg")
    
    # Search query
    query = f"{city} travel landmark architecture"
    
    try:
        # Fetch image
        print(f"Fetching image for: {query}")
        image_data = fetch_unsplash_image(query, api_key)
        
        # Process and save image
        print(f"Processing image and saving to: {output_path}")
        process_image(image_data, output_path)
        
        print("Image processing completed successfully")
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fetch_image.py <slug> <city>")
        sys.exit(1)
    
    slug = sys.argv[1]
    city = sys.argv[2]
    
    success = main(slug, city)
    sys.exit(0 if success else 1) 