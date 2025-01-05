import os
import requests
from bs4 import BeautifulSoup
import html2text
import feedparser
import re
from time import sleep
from datetime import datetime
from email.utils import parsedate_to_datetime

# Configuration for multiple blogs
blogs = [
  {
    "name": "rollemaa",
    "feed": "https://www.rollemaa.fi/feed/?paged={}&posts_per_page=50000&post_type=post",
    "output_path": "/home/rolle/Documents/Brain dump/Blogit/rollemaa"
  },
  {
    "name": "rollemaa-lokikirja",
    "feed": "https://www.rollemaa.fi/lokikirja/feed/?paged={}&posts_per_page=50000",
    "output_path": "/home/rolle/Documents/Brain dump/Blogit/rollemaa-lokikirja"
  },
  {
    "name": "rolle.design",
    "feed": "https://rolle.design/feed/?paged={}&posts_per_page=50000",
    "output_path": "/home/rolle/Documents/Brain dump/Blogit/rolle.design"
  },
  {
    "name": "dude.fi",
    "feed": "https://dude.fi/feed/?paged={}&posts_per_page=50000",
    "output_path": "/home/rolle/Documents/Brain dump/Blogit/dude.fi"
  }
  # Your new blog here
  # {
  #   "name": "your-new-blog",
  #   "feed": "https://your-new-blog.com/feed/?paged={}&posts_per_page=50000",
  #   "output_path": "/home/rolle/Documents/Brain dump/Blogit/your-new-blog"
  # }
]

def sanitize_filename(filename):
  filename = re.sub(r'[^\w\s-]', '', filename)
  filename = re.sub(r'[-\s]+', '-', filename)
  return filename.strip('-').lower()

def format_date(date_str):
  try:
    dt = parsedate_to_datetime(date_str)
    return dt.strftime('%Y-%m-%d')
  except:
    try:
      dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
      return dt.strftime('%Y-%m-%d')
    except:
      return 'no-date'

def clean_image_url(url):
  """Get original image URL from pagespeed URL"""
  if not url:
    return ""

  # If URL contains pagespeed, get the original path
  if '.pagespeed.' in url:
    parts = url.split('.pagespeed.')[0]
    # Remove x prefix if exists
    if parts.startswith('x'):
      parts = parts[1:]
    # Get the original extension
    ext = url.split('.')[-1]
    return f"{parts}.{ext}"

  return url

def get_full_post_content(url):
  try:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to get og:image first
    og_image = soup.find('meta', property='og:image')
    featured_image = og_image['content'] if og_image else None

    # Try different common content selectors
    content_selectors = [
      ".entry-content",
      ".gutenberg-content",
      ".site-content article",
      "article",
      ".post-content",
      ".content",
      "main",
      "#content",
      ".article-content",
      "[itemprop='articleBody']"
    ]

    content = None
    for selector in content_selectors:
      content = soup.select_one(selector)
      if content:
        break

    if not content:
      print(f"No content found for {url}. Available classes:", [cls for tag in soup.find_all(class_=True) for cls in tag['class']])
      return None

    # Remove unwanted elements
    for unwanted in [".notification-box", ".author-info", ".post-past"]:
      element = content.select_one(unwanted)
      if element:
        element.decompose()

    reading_time = soup.select_one(".time-to-read")
    reading_time = reading_time.text.strip() if reading_time else None

    categories = [cat.text.strip() for cat in soup.select(".cat-links a")]
    tags = [tag.text.strip() for tag in soup.select(".tags-links a")]

    return {
      'content': content.decode_contents(),
      'reading_time': reading_time,
      'categories': categories,
      'tags': tags,
      'featured_image': featured_image
    }
  except Exception as e:
    print(f"Error fetching {url}: {str(e)}")
    return None

def fetch_and_convert_posts():
  for blog in blogs:
    print(f"\nProcessing blog: {blog['name']}")

    # Create output directory if it doesn't exist
    os.makedirs(blog['output_path'], exist_ok=True)

    page = 1
    total_entries = 0
    processed_urls = set()  # Keep track of processed URLs

    while True:
      current_feed_url = blog['feed'].format(page)
      print(f"Fetching feed page {page}: {current_feed_url}")

      headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }

      try:
        response = requests.get(current_feed_url, headers=headers)
        feed = feedparser.parse(response.text)

        entries = [e for e in feed.entries if e.link not in processed_urls]

        if not entries:
          print(f"No more new entries found after {total_entries} total posts")
          break

        total_entries += len(entries)
        print(f"Found {len(entries)} new entries on page {page}")

        for entry in entries:
          processed_urls.add(entry.link)
          title = entry.title
          content_url = entry.link
          date = format_date(entry.published)

          # Create year and month folders
          year = date[:4]
          month = date[5:7]
          year_path = os.path.join(blog['output_path'], year)
          month_path = os.path.join(year_path, month)
          os.makedirs(month_path, exist_ok=True)

          safe_title = sanitize_filename(title)
          filename = f"{date}-{safe_title}.md"
          filepath = os.path.join(month_path, filename)

          if os.path.exists(filepath):
            print(f"Skipping existing post: {title}")
            continue

          print(f"Fetching full content for: {title}")
          full_post = get_full_post_content(content_url)

          if not full_post:
            print(f"Could not fetch content for: {title}")
            continue

          content_soup = BeautifulSoup(full_post['content'], 'html.parser')

          h2t = html2text.HTML2Text()
          h2t.body_width = 0
          h2t.ignore_emphasis = False
          h2t.single_line_break = False  # Changed to False to preserve paragraph breaks
          h2t.ul_item_mark = '-'  # Consistent list markers
          h2t.inline_links = True
          h2t.wrap_links = False
          markdown_content = h2t.handle(full_post['content'])

          # Replace 3 or more newlines with just 2 newlines (one blank line between paragraphs)
          markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

          # Fix list item spacing: ensure exactly one space before and after the dash
          markdown_content = re.sub(r'^\s*-\s+', ' - ', markdown_content, flags=re.MULTILINE)

          # Add line break before lists
          markdown_content = re.sub(r'([^\n])\n(\s*- )', r'\1\n\n\2', markdown_content)

          # Add line break between image and figcaption
          markdown_content = re.sub(r'(!\[.*?\].*?)(\[.*?\])', r'\1\n\2', markdown_content)

          with open(filepath, "w", encoding='utf-8') as file:
            file.write(f"# {title}\n\n")

            file.write("```embed\n")
            file.write(f'title: "{title}"\n')

            # Use og:image if available, otherwise try content image
            image_url = ""
            if full_post['featured_image']:
              image_url = full_post['featured_image']
            else:
              first_img = content_soup.find('img')
              if first_img and 'src' in first_img.attrs:
                image_url = clean_image_url(first_img['src'])

            file.write(f'image: "{image_url}"\n')

            # Get description from first paragraph
            first_p = content_soup.find('p')
            description = first_p.text.strip() if first_p else ""
            file.write(f'description: "{description}"\n')
            file.write(f'url: "{content_url}"\n')
            file.write("```\n\n")

            file.write(markdown_content)

          print(f"Saved: {year}/{month}/{filename}")
          sleep(1)

        page += 1
        sleep(2)  # Add delay between pages

      except Exception as e:
        print(f"Error on page {page}: {str(e)}")
        break

# Start scraping
fetch_and_convert_posts()
