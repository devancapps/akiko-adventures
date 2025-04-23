#!/usr/bin/env python3
import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime

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

if __name__ == "__main__":
    update_blog_data() 