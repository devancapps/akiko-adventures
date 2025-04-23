#!/usr/bin/env python3
import os
import json
import openai
import datetime
from pathlib import Path
from slugify import slugify
import random

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Constants
BLOG_TEMPLATE_PATH = 'scripts/blog_template.html'
BLOG_OUTPUT_DIR = 'blog'
POSTED_BLOGS_FILE = 'scripts/posted_blogs.json'
BLOG_TOPICS = [
    "Best Hidden Cafes in {city}",
    "A Local's Guide to {city}",
    "How to Spend 48 Hours in {city}",
    "Budget Travel Guide: {city}",
    "{city}'s Most Instagram-Worthy Spots",
    "Where to Stay in {city}: Best Neighborhoods",
    "Street Food Guide: {city}",
    "Top 10 Things to Do in {city}",
    "Off the Beaten Path: {city}",
    "Best Time to Visit {city}"
]

CITIES = [
    "Tokyo", "Kyoto", "Osaka", "Seoul", "Bangkok", "Singapore",
    "London", "Paris", "Barcelona", "Rome", "Amsterdam", "Berlin",
    "New York", "San Francisco", "Vancouver", "Sydney", "Melbourne",
    "Dubai", "Istanbul", "Hong Kong"
]

def load_posted_blogs():
    """Load the list of previously posted blog slugs."""
    if os.path.exists(POSTED_BLOGS_FILE):
        with open(POSTED_BLOGS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_posted_blogs(posted_blogs):
    """Save the updated list of posted blog slugs."""
    with open(POSTED_BLOGS_FILE, 'w') as f:
        json.dump(posted_blogs, f, indent=2)

def generate_blog_content(topic, city):
    """Generate blog content using OpenAI's API."""
    prompt = f"""Write a detailed travel blog post about {topic}.
    Include:
    - An engaging introduction
    - At least 3 main sections with subheadings
    - Practical tips and recommendations
    - Local insights and cultural notes
    - Budget considerations
    - Best times to visit
    - Transportation tips
    
    Format the content in HTML with proper semantic tags (<h2>, <p>, <ul>, etc).
    Include relevant emojis at the start of each section.
    Make it informative, engaging, and SEO-friendly.
    Word count: 1000-1500 words."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional travel writer creating engaging, informative blog content."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def generate_meta_description(content):
    """Generate a meta description using OpenAI."""
    prompt = f"Generate a compelling 155-character meta description for this travel blog post that includes main keywords and encourages clicks. Content: {content[:500]}..."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SEO expert writing meta descriptions."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def create_blog_post():
    """Create a new blog post."""
    # Load previously posted blogs
    posted_blogs = load_posted_blogs()
    
    # Select random city and topic template
    city = random.choice(CITIES)
    topic_template = random.choice(BLOG_TOPICS)
    topic = topic_template.format(city=city)
    
    # Generate slug
    slug = slugify(topic)
    
    # Check if this topic has been done before
    if slug in posted_blogs:
        print(f"Topic '{topic}' has already been covered. Trying again...")
        return None
    
    # Generate content
    content = generate_blog_content(topic, city)
    description = generate_meta_description(content)
    
    # Calculate read time (assume 200 words per minute)
    word_count = len(content.split())
    read_time = max(1, round(word_count / 200))
    
    # Load template
    with open(BLOG_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    # Current date
    date = datetime.datetime.now().strftime('%B %d, %Y')
    
    # Replace placeholders
    blog_html = template.format(
        title=topic,
        description=description,
        slug=slug,
        image_alt=f"Travel guide to {city}",
        date=date,
        read_time=read_time,
        destination=city,
        content=content
    )
    
    # Save the blog post
    output_path = os.path.join(BLOG_OUTPUT_DIR, f"{slug}.html")
    with open(output_path, 'w') as f:
        f.write(blog_html)
    
    # Update posted blogs
    posted_blogs.append(slug)
    save_posted_blogs(posted_blogs)
    
    print(f"Created blog post: {output_path}")
    return {
        "title": topic,
        "slug": slug,
        "description": description,
        "date": date
    }

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    blog_info = create_blog_post()
    if blog_info:
        print(f"Successfully generated blog: {blog_info['title']}")
        print(f"Slug: {blog_info['slug']}")
        print(f"Description: {blog_info['description']}")
    else:
        print("Failed to generate blog post") 