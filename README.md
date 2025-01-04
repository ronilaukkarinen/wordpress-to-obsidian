# WordPress to Obsidian Converter

A Python script to convert WordPress blog posts to Markdown files for Obsidian. The script fetches posts from WordPress RSS feeds and organizes them into a year/month folder structure.

## Features

- Fetches posts from multiple WordPress RSS feeds
- Converts HTML content to Markdown
- Extracts featured images and metadata
- Organizes posts into YYYY/MM folders
- Supports Obsidian Link embed plugin embed blocks
- Handles pagespeed-optimized image URLs
- Prevents duplicate downloads
- Includes progress tracking

## How to use

Install required packages first:

```bash
pip install requests beautifulsoup4 html2text feedparser
```

Edit scraper.py, add your blog feeds and output paths.

Run the script:

```bash
python scraper.py
```

If you are using [headless Obsidian and sync](https://rolle.design/setting-up-a-headless-obsidian-instance-for-syncing) you can add a cronjob for backing up your blog posts automatically to Obsidian:

```bash
crontab -e
```

Add this line to the end of the file:

```bash
0 0 * * * /usr/bin/python3 /home/rolle/wordpress-to-obsidian/scraper.py > /tmp/wordpress-to-obsidian.log 2>&1
```
