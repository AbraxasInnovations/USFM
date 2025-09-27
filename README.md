# US Financial Moves

A comprehensive US Finance Deal Feed platform featuring real-time news ingestion, automated content processing, and a modern web interface.

## 🚀 Features

### Frontend
- **Morning Brew Style Layout**: Featured article + top headlines
- **Section-Based Navigation**: M&A, LBO/PE, Regulatory, Capital Markets, DeFi/Crypto
- **Global Search**: Server-side search across titles, summaries, and tags
- **Tag-Based Filtering**: Clickable tags for content discovery
- **Archive System**: Paginated browsing of older posts
- **Responsive Design**: Mobile-friendly interface
- **Real-Time Updates**: ISR with 60-second revalidation

### Backend
- **Automated News Ingestion**: Hourly RSS feed processing
- **Content Processing**: Smart section classification and tag extraction
- **Deduplication**: Prevents duplicate content using content hashing
- **Legal Compliance**: Only stores ≤75-word excerpts with proper attribution
- **Fan-out Delivery**: Web revalidation and social media queuing
- **Storage Management**: Automatic cleanup to stay within limits

### Technology Stack
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Supabase (PostgreSQL), Python
- **Deployment**: Vercel, GitHub Actions
- **Content Sources**: RSS feeds (MarketWatch, Reuters, etc.)

## 📊 Live Demo

Visit the live site: [US Financial Moves](https://your-domain.vercel.app)

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- GitHub account
- Vercel account

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/us-financial-moves.git
cd us-financial-moves
```

2. **Run the setup script**
```bash
./setup.sh
```

3. **Install dependencies**
```bash
npm install
```

4. **Set up environment variables**
```bash
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials
```

5. **Start the development server**
```bash
npm run dev
```

6. **Test the ingestor system**
```bash
cd ingestor
python test_reliable_feeds.py
```

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 📁 Project Structure

```
us-financial-moves/
├── app/                    # Next.js App Router
│   ├── api/revalidate/     # Revalidation endpoint
│   ├── archive/           # Archive page
│   ├── search/            # Search page
│   ├── section/[slug]/    # Section pages
│   ├── tag/[tag]/         # Tag pages
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── Header.tsx         # Navigation header
│   ├── PostCard.tsx       # Post display component
│   ├── FeaturedArticle.tsx # Featured article component
│   ├── TopHeadlines.tsx   # Top headlines component
│   └── SectionNewsGrid.tsx # Section news grid
├── ingestor/              # Python news ingestion system
│   ├── main.py           # Main ingestion script
│   ├── feed_reader.py    # RSS feed processing
│   ├── content_processor.py # Content normalization
│   ├── database.py       # Supabase integration
│   └── delivery_worker.py # Delivery processing
├── .github/workflows/     # GitHub Actions
│   ├── news-ingestion.yml # Hourly news ingestion
│   └── delivery-worker.yml # Delivery processing
└── lib/                   # Utilities
    └── supabase.ts       # Supabase client
```

## 🔧 Configuration

### Content Sources
Edit `ingestor/config.py` to add or modify RSS feeds:

```python
CONTENT_SOURCES = {
    'financial_news': [
        {
            'name': 'MarketWatch - Top Stories',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'cap',
            'tags': ['markets', 'finance']
        }
    ]
}
```

### Scraping Frequency
- **Current**: Every hour (respects free tier limits)
- **Configurable**: Edit GitHub Actions cron schedule
- **Recommended**: 30-60 minutes for optimal freshness

## 📈 Monitoring

### GitHub Actions
- **News Ingestion**: Runs every hour
- **Delivery Worker**: Runs every 5 minutes
- **Logs**: Available in Actions tab

### Supabase Dashboard
- **Database**: Monitor storage usage
- **API**: Track request volume
- **Logs**: View database operations

### Vercel Dashboard
- **Functions**: Monitor revalidation calls
- **Analytics**: Track page views
- **Logs**: View function execution

## 🔒 Security & Compliance

### Content Usage
- **Fair Use**: Only excerpts (≤75 words) are stored
- **Attribution**: All content includes source attribution
- **No Full Articles**: Respects publisher terms of service

### Data Protection
- **Environment Variables**: All secrets stored securely
- **Rate Limiting**: Respects RSS feed providers
- **Error Handling**: Comprehensive retry logic

## 📊 Performance

### Supabase Free Tier Limits
- **Database**: 500MB storage
- **Bandwidth**: 5GB egress
- **API Requests**: Unlimited
- **Concurrent Connections**: 200

### Optimization Features
- **ISR Caching**: 60-second revalidation
- **Content Deduplication**: Prevents duplicate posts
- **Automatic Cleanup**: Removes old content
- **Batch Processing**: Efficient database operations

## 🚀 Scaling

### Upgrade Path
1. **Supabase Pro**: $25/month for 8GB database
2. **GitHub Pro**: $4/month for more Actions minutes
3. **Vercel Pro**: $20/month for more bandwidth

### Performance Improvements
- **More Content Sources**: Add additional RSS feeds
- **Faster Ingestion**: Increase scraping frequency
- **Enhanced Processing**: Add AI summarization
- **Social Media**: Enable X/Twitter posting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- **No new content**: Check GitHub Actions logs
- **Database errors**: Verify Supabase credentials
- **Deployment issues**: Check Vercel function logs

### Getting Help
- **Documentation**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic news ingestion
- ✅ Web interface
- ✅ Search and filtering
- ✅ Automated deployment

### Phase 2 (Future)
- 🔄 AI-powered content summarization
- 🔄 Enhanced social media integration
- 🔄 Advanced analytics dashboard
- 🔄 Mobile app

### Phase 3 (Long-term)
- 🔄 Real-time notifications
- 🔄 Custom user preferences
- 🔄 Advanced content curation
- 🔄 API for third-party integrations

## 📊 Success Metrics

After deployment, you should see:
- ✅ New posts appearing hourly
- ✅ Content properly categorized
- ✅ Search functionality working
- ✅ No duplicate content
- ✅ All articles linking to sources
- ✅ Mobile-responsive design
- ✅ Fast page load times

---

**Built with ❤️ for the financial community**

*Stay informed with the latest US financial moves, deals, and market developments.*
