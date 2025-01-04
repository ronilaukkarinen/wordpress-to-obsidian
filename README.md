# WordPress to Obsidian converter

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
0 0 * * * /usr/bin/python3 /home/rolle/wordpress-to-obsidian/scraper.py >> /tmp/wordpress-to-obsidian.log 2>&1
```

## For Pyenv

If you are using pyenv, you can install the required packages in the virtual environment:

```bash
sudo apt install python3-full python3-venv
cd /home/rolle/wordpress-to-obsidian
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 html2text feedparser
python scraper.py
```

Add helper script for running the script in the virtual environment:

```bash
echo 'source /home/rolle/wordpress-to-obsidian/venv/bin/activate && python /home/rolle/wordpress-to-obsidian/scraper.py' > wordpress-to-obsidian
sudo mv wordpress-to-obsidian /usr/local/bin/
sudo chmod +x /usr/local/bin/wordpress-to-obsidian
```

Then the cronjob can be added like this:

```bash
0 0 * * * /usr/local/bin/wordpress-to-obsidian >> /tmp/wordpress-to-obsidian.log 2>&1 > /dev/null
```
