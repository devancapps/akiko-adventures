#!/usr/bin/env python3
import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_blog_info(html_file):
    """Extract blog information from HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Get title
        title = soup.title.string.replace(' - Akiko Adventures', '')
        
        # Get description
        description = soup.find('meta', {'name': 'description'})['content']
        
        # Get image
        image = soup.find('img', class_='blog-hero-image')['src']
        
        # Get date
        date_span = soup.find('i', class_='far fa-calendar-alt').parent
        date_str = date_span.text.strip()
        date = datetime.strptime(date_str, '%B %d, %Y')
        
        return {
            'title': title,
            'excerpt': description,
            'image': image.replace('..', ''),
            'link': f"/blog/{os.path.basename(html_file)}",
            'date': date.strftime('%Y-%m-%d')
        }

def update_blog_data():
    """Update the blogData.js file with latest blog posts."""
    # Get all blog HTML files
    blog_files = glob.glob('blog/*.html')
    
    # Skip index.html
    blog_files = [f for f in blog_files if 'index.html' not in f]
    
    # Extract info from each blog
    blogs = []
    for file in blog_files:
        try:
            blog_info = extract_blog_info(file)
            blogs.append(blog_info)
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    # Sort by date, newest first
    blogs.sort(key=lambda x: x['date'], reverse=True)
    
    # Keep only the latest 9 posts
    blogs = blogs[:9]
    
    # Generate JavaScript
    js_content = """// Auto-generated blog data
const blogData = %s;

export default blogData;
""" % json.dumps(blogs, indent=2)
    
    # Save to file
    with open('blog/blogData.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Updated blogData.js with {len(blogs)} posts")
    return blogs

def get_blog_metadata(blog_path):
    """Extract metadata from a blog post HTML file."""
    try:
        with open(blog_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        return {
            'title': soup.find('title').text.replace(' - Akiko Adventures', ''),
            'description': soup.find('meta', {'name': 'description'})['content'],
            'date': soup.find('span', {'class': 'blog-meta'}).find('span').text,
            'read_time': soup.find_all('span', {'class': 'blog-meta'})[1].text,
            'image': soup.find('div', {'class': 'blog-hero'}).find('img')['src'],
            'url': f"/blog/{os.path.basename(blog_path)}"
        }
    except Exception as e:
        logger.error(f"Error extracting metadata from {blog_path}: {str(e)}")
        return None

def update_blog_index(blog_dir='../blog', index_path='../blog/index.html'):
    """Update the blog index page with the latest posts."""
    try:
        # Get all blog posts
        blog_posts = []
        for filename in os.listdir(blog_dir):
            if filename.endswith('.html') and filename != 'index.html':
                blog_path = os.path.join(blog_dir, filename)
                metadata = get_blog_metadata(blog_path)
                if metadata:
                    blog_posts.append(metadata)
        
        # Sort by date (newest first)
        blog_posts.sort(key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'), reverse=True)
        
        # Keep only the 9 most recent posts
        blog_posts = blog_posts[:9]
        
        # Read the index template
        with open(index_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find the blog grid container
        blog_grid = soup.find('div', {'class': 'blog-grid'})
        if not blog_grid:
            logger.error("Blog grid container not found in index.html")
            return False
        
        # Clear existing blog cards
        for card in blog_grid.find_all('div', {'class': 'blog-card'}):
            card.decompose()
        
        # Add new blog cards
        for post in blog_posts:
            card_html = f"""
            <div class="blog-card">
                <a href="{post['url']}">
                    <img src="{post['image']}" alt="{post['title']}">
                    <div class="blog-card-content">
                        <h3>{post['title']}</h3>
                        <p>{post['description']}</p>
                        <div class="blog-meta">
                            <span><i class="far fa-calendar-alt mr-2"></i>{post['date']}</span>
                            <span><i class="far fa-clock mr-2"></i>{post['read_time']}</span>
                        </div>
                    </div>
                </a>
            </div>
            """
            blog_grid.append(BeautifulSoup(card_html, 'html.parser'))
        
        # Update the last updated date
        last_updated = soup.find('div', {'class': 'last-updated'})
        if last_updated:
            last_updated.string = f"Last updated: {datetime.now().strftime('%B %d, %Y')}"
        
        # Save the updated index
        with open(index_path, 'w') as f:
            f.write(str(soup))
        
        logger.info("Successfully updated blog index")
        return True
    except Exception as e:
        logger.error(f"Error updating blog index: {str(e)}")
        return False

if __name__ == "__main__":
    update_blog_data()
    update_blog_index() 