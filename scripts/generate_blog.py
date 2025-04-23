#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from openai import OpenAI
from slugify import slugify
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import traceback
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_blog_content(topic):
    """Generate blog content using OpenAI API."""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return None

        client = OpenAI(api_key=openai_key)
        
        prompt = f"""Write a detailed blog post about {topic}. Include the following sections:
        1. Introduction
        2. Main content with at least 3 subsections
        3. Tips and recommendations
        4. Conclusion

        Format the response as a JSON object with the following structure:
        {{
            "title": "The main title of the blog post",
            "slug": "url-friendly-version-of-title",
            "metadata": {{
                "description": "A brief description for SEO",
                "keywords": ["keyword1", "keyword2", "etc"],
                "author": "Akiko"
            }},
            "content": "The full HTML content of the blog post",
            "structured_data": {{
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": "The main title of the blog post",
                "description": "A brief description for SEO",
                "author": {{
                    "@type": "Person",
                    "name": "Akiko"
                }},
                "datePublished": "Current date in ISO format",
                "image": "URL to the main image"
            }}
        }}
        """

        logger.info("Making request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a travel blogger writing engaging, informative content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        try:
            content = response.choices[0].message.content
            logger.debug(f"Content from OpenAI: {content}")
            
            blog_data = json.loads(content)
            logger.info("Successfully parsed blog data from OpenAI response")

            # Validate required fields
            required_fields = ['title', 'slug', 'metadata', 'content', 'structured_data']
            for field in required_fields:
                if field not in blog_data:
                    logger.error(f"Missing required field in blog data: {field}")
                    return None

            required_metadata = ['description', 'keywords', 'author']
            for field in required_metadata:
                if field not in blog_data['metadata']:
                    logger.error(f"Missing required metadata field: {field}")
                    return None

            return blog_data

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding OpenAI response JSON: {str(e)}")
            logger.debug(f"Raw response content: {content}")
            return None
        except KeyError as e:
            logger.error(f"Missing key in OpenAI response: {str(e)}")
            logger.debug(f"Response data: {response}")
            return None

    except Exception as e:
        logger.error(f"Error generating blog content: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
        return None

def generate_description(title, content):
    """Generate a description from the title and content."""
    # Take the first 200 characters of content, strip HTML, and end at a sentence
    text = BeautifulSoup(content, 'html.parser').get_text()
    description = text[:200].strip()
    last_sentence = description.rfind('.')
    if last_sentence > 0:
        description = description[:last_sentence + 1]
    return description

def estimate_read_time(content):
    """Estimate reading time in minutes based on content length."""
    # Average reading speed is about 200-250 words per minute
    words = len(BeautifulSoup(content, 'html.parser').get_text().split())
    minutes = max(1, round(words / 200))
    return minutes

def fetch_pexels_image(query):
    """Fetch a relevant image from Pexels with fallback to default image."""
    try:
        api_key = os.getenv('PEXELS_API_KEY')
        if not api_key:
            logger.error("PEXELS_API_KEY not found in environment variables")
            return get_default_image(query)

        headers = {
            "Authorization": api_key
        }
        logger.info(f"Searching Pexels for images matching: {query}")
        
        # URL encode the query
        encoded_query = requests.utils.quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&orientation=landscape&per_page=1"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            logger.error("Invalid Pexels API key")
            return get_default_image(query)
        
        if response.status_code != 200:
            logger.error(f"Pexels API error: Status {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            return get_default_image(query)
            
        data = response.json()
        
        if not data.get('photos'):
            logger.warning(f"No images found for query: {query}")
            return get_default_image(query)
            
        photo = data['photos'][0]
        image_url = photo['src']['large']
        photographer = photo.get('photographer', 'Unknown')
        logger.info(f"Found image by {photographer}: {image_url}")
        
        image_response = requests.get(image_url)
        
        if image_response.status_code != 200:
            logger.error(f"Failed to download image: {image_response.status_code}")
            return get_default_image(query)
            
        # Save image to assets directory
        os.makedirs('assets/destinations', exist_ok=True)
        image_path = f"assets/destinations/{slugify(query)}.jpg"
        
        with open(image_path, 'wb') as f:
            f.write(image_response.content)
        
        logger.info(f"Successfully downloaded and saved image to {image_path}")
        return image_path
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching image: {str(e)}")
        return get_default_image(query)
    except Exception as e:
        logger.error(f"Error fetching Pexels image: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
        return get_default_image(query)

def get_default_image(query):
    """Get a default image based on the query."""
    try:
        # Map common travel destinations to default images
        default_images = {
            'tokyo': 'tokyo-hotel-preview.jpg',
            'kyoto': 'kyoto-temple.jpg',
            'osaka': 'osaka-castle.jpg',
            'london': 'london-bridge.jpg',
            'paris': 'eiffel-tower.jpg',
            'new york': 'new-york-city.jpg',
            'sydney': 'sydney-opera.jpg',
            'bangkok': 'bangkok-temple.jpg',
            'seoul': 'seoul-palace.jpg',
            'shanghai': 'shanghai-skyline.jpg'
        }
        
        # Try to find a matching default image
        query_lower = query.lower()
        for key, image in default_images.items():
            if key in query_lower:
                return f"assets/{image}"
        
        # If no match found, use the generic blog placeholder
        return os.getenv('DEFAULT_BLOG_IMAGE_URL', '/assets/blog-placeholder.jpg')
    except Exception as e:
        logger.error(f"Error getting default image: {str(e)}")
        return os.getenv('DEFAULT_BLOG_IMAGE_URL', '/assets/blog-placeholder.jpg')

def create_blog_html(blog_data, image_path):
    """Create HTML file for the blog post."""
    try:
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{blog_data['metadata']['description']}">
    <meta property="og:title" content="{blog_data['title']}">
    <meta property="og:description" content="{blog_data['metadata']['description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://akiko-adventures.web.app/blog/{blog_data['slug']}.html">
    <meta property="og:image" content="https://akiko-adventures.web.app/{image_path}">
    <title>{blog_data['title']} - Akiko Adventures</title>
    <link rel="canonical" href="https://akiko-adventures.web.app/blog/{blog_data['slug']}.html">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="./blog-styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(blog_data['structured_data'])}
    </script>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="logo">Akiko Adventures</a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/blog/index.html" class="active">Blog</a>
                <a href="/resources/index.html">Resources</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="blog-hero">
        <img src="../{image_path}" alt="{blog_data['title']}">
        <div class="blog-hero-content">
            <div class="container mx-auto px-4">
                <h1 class="text-4xl md:text-5xl font-bold mb-4">{blog_data['title']}</h1>
                <div class="blog-meta">
                    <span><i class="far fa-calendar-alt mr-2"></i>{datetime.now().strftime('%B %d, %Y')}</span>
                    <span><i class="far fa-clock mr-2"></i>{blog_data['metadata'].get('read_time', 5)} min read</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <article class="max-w-3xl mx-auto">
            {blog_data['content']}
            
            <!-- Affiliate Notice -->
            <div class="affiliate-notice">
                <p>
                    <i class="fas fa-info-circle mr-2"></i>
                    <strong>Affiliate Disclosure:</strong> This article contains affiliate links. If you make a booking through these links, we may earn a commission at no extra cost to you. This helps us continue providing valuable travel content.
                </p>
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="container mx-auto px-4">
            <div class="text-center">
                <p class="mb-4">© {datetime.now().year} Akiko Adventures. All rights reserved.</p>
                <p class="text-sm text-gray-400">
                    <i class="fas fa-link mr-2"></i>
                    This site contains affiliate links. We may earn a commission when you make a purchase through these links.
                </p>
            </div>
        </div>
    </footer>
</body>
</html>"""

        # Save the HTML file
        os.makedirs('blog', exist_ok=True)
        with open(f"blog/{blog_data['slug']}.html", 'w') as f:
            f.write(template)
        
        return True
    except Exception as e:
        logger.error(f"Error creating blog HTML: {str(e)}")
        return False

def create_index_template():
    """Create the initial index.html template if it doesn't exist."""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Blog</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Travel Adventures</h1>
        <nav>
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
        </nav>
    </header>
    <main>
        <div class="blog-posts">
            <!-- Blog posts will be inserted here -->
        </div>
    </main>
    <footer>
        <p>&copy; 2024 Travel Adventures. All rights reserved.</p>
    </footer>
</body>
</html>"""
    
    try:
        os.makedirs('blog', exist_ok=True)
        with open('blog/index.html', 'w') as f:
            f.write(template)
        logger.info("Created new index.html template")
        return True
    except Exception as e:
        logger.error(f"Failed to create index.html template: {str(e)}")
        return False

def update_blog_index(blog_data, image_path):
    """This function is now deprecated as we're updating the index.html directly."""
    return True

def update_blog_data(blog_data, image_path):
    """Update the blog data in index.html with the new post."""
    try:
        def escape_string(s):
            """Escape special characters for JavaScript strings."""
            return (s.replace('\\', '\\\\')
                    .replace("'", "\\'")
                    .replace('"', '\\"')
                    .replace('\n', '\\n')
                    .replace('\r', '\\r')
                    .replace('\t', '\\t'))
        
        # Create new blog post entry
        new_post = {
            'title': blog_data['title'],
            'excerpt': blog_data['metadata']['description'],
            'image': f"../{image_path}",
            'link': f"{blog_data['slug']}.html",
            'date': datetime.now().strftime('%B %d, %Y')
        }
        
        # Read the current index.html
        with open('blog/index.html', 'r') as f:
            content = f.read()
        
        # Find the blogData array in the content
        blog_data_match = re.search(r'const blogData = \[([\s\S]*?)\];', content)
        if not blog_data_match:
            logger.error("Could not find blogData array in index.html")
            return False
        
        # Parse existing blog posts
        existing_data = blog_data_match.group(1).strip()
        if existing_data:
            # Split by closing brace to get individual post objects
            posts = [p.strip() + '}' for p in existing_data.split('}') if p.strip()]
            # Remove the last '}' from the last post
            posts[-1] = posts[-1][:-1]
        else:
            posts = []
        
        # Format the new post
        new_post_str = (
            "    {\n"
            f"        'title': '{escape_string(new_post['title'])}',\n"
            f"        'excerpt': '{escape_string(new_post['excerpt'])}',\n"
            f"        'image': '{new_post['image']}',\n"
            f"        'link': '{new_post['link']}',\n"
            f"        'date': '{new_post['date']}'\n"
            "    }"
        )
        
        # Add new post at the beginning
        if posts:
            posts.insert(0, new_post_str + ',')
        else:
            posts.insert(0, new_post_str)
        
        # Create the updated blogData array
        updated_data = 'const blogData = [\n' + '\n'.join(posts) + '\n];'
        
        # Replace the old blogData array with the new one
        updated_content = re.sub(
            r'const blogData = \[[\s\S]*?\];',
            updated_data,
            content
        )
        
        # Write the updated content back to index.html
        with open('blog/index.html', 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully updated blog data in index.html")
        return True
        
    except Exception as e:
        logger.error(f"Error updating blog data: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
        return False

def main():
    """Main function to generate a blog post."""
    try:
        # Set the topic for the blog post
        topic = "Exploring Busan: South Korea's Vibrant Coastal City"
        logger.info(f"Generating blog post about: {topic}")
        
        # Generate blog content
        blog_data = generate_blog_content(topic)
        if not blog_data:
            logger.error("Failed to generate blog content")
            return
        
        # Fetch image
        image_path = fetch_pexels_image(topic)
        
        # Create blog HTML
        if not create_blog_html(blog_data, image_path):
            logger.error("Failed to create blog HTML")
            return
        
        # Update blog data
        if not update_blog_data(blog_data, image_path):
            logger.error("Failed to update blog data")
            return
        
        # Update blog index
        if not update_blog_index(blog_data, image_path):
            logger.error("Failed to update blog index")
            return
        
        logger.info("Successfully created and published blog post")
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main() 