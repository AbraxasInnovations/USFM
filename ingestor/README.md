# News Ingestor System

This system automatically fetches financial news from RSS feeds and stores them in the Supabase database for the US Financial Moves platform.

## Features

- **Automated RSS Feed Processing**: Fetches news from multiple financial sources
- **Content Normalization**: Processes and cleans content for consistent storage
- **Deduplication**: Prevents duplicate posts using content hashing
- **Section Classification**: Automatically categorizes content into appropriate sections
- **Tag Extraction**: Generates relevant tags for better discoverability
- **Fan-out Delivery**: Queues content for web revalidation and social media posting
- **Storage Management**: Automatically cleans up old content to stay within limits

## Content Sources

The system currently fetches from:

### Financial News
- Yahoo Finance - Business
- MarketWatch - Top Stories  
- Reuters - Business News

### Mergers & Acquisitions
- Yahoo Finance - Mergers & Acquisitions

### Regulatory
- DOJ Antitrust Division RSS
- FTC News RSS

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Configuration

### Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `REVALIDATE_URL`: Next.js revalidation endpoint URL
- `REVALIDATE_SECRET`: Secret for revalidation endpoint
- `X_ENABLED`: Enable X/Twitter posting (true/false)
- `X_BEARER`: X/Twitter bearer token (if enabled)

### Content Sources

Edit `config.py` to add or modify content sources. Each source should have:
- `name`: Display name for the source
- `url`: RSS feed URL
- `section`: Default section (ma, lbo, reg, cap, rumor)
- `tags`: Default tags for content from this source

## Usage

### Manual Execution

Run the ingestor manually:
```bash
python main.py
```

Run the delivery worker manually:
```bash
python delivery_worker.py
```

### Automated Execution

The system is designed to run via GitHub Actions:

- **News Ingestion**: Runs every hour (`0 * * * *`)
- **Delivery Worker**: Runs every 5 minutes (`*/5 * * * *`)

## Content Processing

### Excerpt Limiting
All content excerpts are limited to 75 words to comply with fair use guidelines.

### Section Classification
Content is automatically classified into sections based on keywords:
- **M&A**: merger, acquisition, acquire, merge, takeover, buyout, deal
- **LBO/PE**: private equity, lbo, leveraged buyout, pe firm
- **Regulatory**: antitrust, ftc, doj, regulatory, approval, investigation
- **Capital Markets**: ipo, public offering, stock, equity, debt, bond, securities
- **Default**: Capital Markets for general financial news

### Tag Extraction
Tags are automatically generated based on content analysis, including:
- Industry tags (ai, tech, healthcare, energy, finance, retail, etc.)
- Deal type tags (acquisition, merger, ipo, antitrust, etc.)
- Source-provided tags

## Database Schema

### Posts Table
- `id`: UUID primary key
- `title`: Post title
- `summary`: Why it matters (1-liner)
- `excerpt`: Quoted content (≤75 words)
- `source_name`: Source publication name
- `source_url`: Original article URL
- `section_slug`: Section classification
- `tags`: Array of relevant tags
- `content_hash`: SHA256 hash for deduplication
- `status`: published/hidden
- `origin_type`: RSS/USGOV/PRESS/MEDIA/RUMOR

### Deliveries Table
- `id`: UUID primary key
- `post_id`: Reference to posts table
- `channel`: web/x
- `payload`: JSON payload for delivery
- `status`: queued/sent/failed/held
- `attempts`: Number of delivery attempts
- `last_error`: Last error message

## Monitoring

### Logs
- `ingestor.log`: Main ingestion process logs
- `delivery_worker.log`: Delivery processing logs

### Statistics
The system tracks:
- Feeds processed
- Entries fetched
- Posts created/skipped
- Delivery success/failure rates
- Error counts

### Supabase Limits
The system is designed to stay within Supabase free tier limits:
- **Database Storage**: 500 MB (with automatic cleanup)
- **Bandwidth**: 5 GB egress (with request optimization)
- **API Requests**: Unlimited (with rate limiting)

## Error Handling

- **Retry Logic**: Failed deliveries are retried up to 5 times
- **Exponential Backoff**: Increasing delays between retries
- **Graceful Degradation**: System continues processing even if individual sources fail
- **Comprehensive Logging**: All errors are logged for debugging

## Legal Compliance

- **Fair Use**: Only excerpts (≤75 words) are stored, not full articles
- **Attribution**: All content includes proper source attribution
- **Publisher Terms**: Respects robots.txt and terms of service
- **Rate Limiting**: Delays between requests to avoid overwhelming sources

## Future Enhancements

- **AI Summarization**: Enhanced content summarization
- **Sentiment Analysis**: Content sentiment scoring
- **Image Processing**: Extract and store relevant images
- **Social Media Integration**: Full X/Twitter posting implementation
- **Analytics**: Content performance tracking
- **Content Moderation**: Automated content filtering
