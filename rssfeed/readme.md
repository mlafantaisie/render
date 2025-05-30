# WoWhead News Reader

Personal RSS Feed Reader for WoWhead news, filtered for patch notes, expansion updates, etc.

## Features
- Pulls and filters news from WoWhead RSS feed
- Stores filtered articles locally
- Private login
- Deployable via Docker on Render
- Scheduled background refresh

## Setup

1. Clone the repo
2. Create `.env` from `.env.example`
3. Build and run:
   ```bash
   docker build -t wowhead-news-reader .
   docker run -p 8000:8000 --env-file .env wowhead-news-reader
