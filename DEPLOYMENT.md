# US Financial Moves - Deployment Guide

This guide will help you deploy the US Financial Moves platform with live news ingestion to production.

## Prerequisites

- GitHub account
- Supabase account (free tier)
- Vercel account (free tier)

## Step 1: GitHub Repository Setup

### 1.1 Create GitHub Repository
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `us-financial-moves` (or your preferred name)
3. Make it public or private (your choice)
4. Don't initialize with README (we already have files)

### 1.2 Push Code to GitHub
```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/us-financial-moves.git

# Push the code
git branch -M main
git push -u origin main
```

## Step 2: GitHub Secrets Configuration

### 2.1 Add Repository Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

#### Supabase Configuration
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

#### Revalidation Configuration
- `REVALIDATE_URL`: Your production domain + `/api/revalidate`
- `REVALIDATE_SECRET`: A secure random string (generate with: `openssl rand -hex 32`)

#### Social Media (Optional)
- `X_ENABLED`: `false` (for now)
- `X_BEARER`: Your X/Twitter bearer token (if you want to enable later)

### 2.2 Generate Revalidation Secret
```bash
# Generate a secure secret
openssl rand -hex 32
```

## Step 3: Vercel Deployment

### 3.1 Deploy to Vercel
1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Configure environment variables in Vercel dashboard:

#### Environment Variables for Vercel
- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anon key
- `REVALIDATE_SECRET`: Same secret you used in GitHub

### 3.2 Update Revalidation URL
After Vercel deployment, update the `REVALIDATE_URL` in GitHub secrets:
- Format: `https://your-domain.vercel.app/api/revalidate`

## Step 4: Enable GitHub Actions

### 4.1 Verify Workflows
1. Go to your GitHub repository → Actions tab
2. You should see two workflows:
   - "News Ingestion" (runs every hour)
   - "Delivery Worker" (runs every 5 minutes)

### 4.2 Manual Test Run
1. Go to Actions → News Ingestion
2. Click "Run workflow" to test manually
3. Check the logs to ensure it's working

## Step 5: Monitor and Verify

### 5.1 Check Database
1. Go to your Supabase dashboard
2. Check the `posts` table for new entries
3. Verify content is being added hourly

### 5.2 Check Website
1. Visit your Vercel deployment
2. Verify new content appears on the homepage
3. Check that sections and tags are working

### 5.3 Monitor Logs
1. GitHub Actions logs show ingestion status
2. Vercel function logs show revalidation status
3. Supabase logs show database operations

## Step 6: Production Optimization

### 6.1 Adjust Scraping Frequency
- **Current**: Every hour (good for free tier)
- **If you upgrade Supabase**: Can increase to every 30 minutes
- **If you upgrade GitHub**: Can increase to every 15 minutes

### 6.2 Add More Content Sources
Edit `ingestor/config.py` to add more RSS feeds:
```python
CONTENT_SOURCES = {
    'financial_news': [
        # Add more sources here
    ]
}
```

### 6.3 Enable Social Media
1. Get X/Twitter API credentials
2. Set `X_ENABLED=true` in GitHub secrets
3. Add `X_BEARER` token

## Troubleshooting

### Common Issues

#### 1. GitHub Actions Failing
- Check that all secrets are set correctly
- Verify Supabase credentials are valid
- Check the Actions logs for specific errors

#### 2. No New Content Appearing
- Verify RSS feeds are accessible
- Check that content is being inserted into database
- Ensure revalidation is working

#### 3. Supabase Limits Exceeded
- Check database size in Supabase dashboard
- Reduce `MAX_POSTS_PER_SOURCE` in config
- Increase cleanup frequency

#### 4. Vercel Function Errors
- Check Vercel function logs
- Verify environment variables are set
- Ensure revalidation secret matches

### Monitoring Commands

```bash
# Check recent posts in database
# (Use Supabase SQL editor)
SELECT COUNT(*) FROM posts WHERE created_at > NOW() - INTERVAL '24 hours';

# Check delivery queue
SELECT COUNT(*) FROM deliveries WHERE status = 'queued';

# Check failed deliveries
SELECT * FROM deliveries WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;
```

## Security Considerations

1. **Environment Variables**: Never commit secrets to git
2. **Rate Limiting**: Respect RSS feed providers' terms
3. **Content Attribution**: Always include source attribution
4. **Legal Compliance**: Only store excerpts, not full articles

## Scaling Considerations

### Free Tier Limits
- **Supabase**: 500MB database, 5GB bandwidth
- **GitHub Actions**: 2000 minutes/month
- **Vercel**: 100GB bandwidth, 100 serverless functions

### Upgrade Path
1. **Supabase Pro**: $25/month for 8GB database
2. **GitHub Pro**: $4/month for more Actions minutes
3. **Vercel Pro**: $20/month for more bandwidth

## Support

If you encounter issues:
1. Check the logs in GitHub Actions
2. Verify all environment variables are set
3. Test the ingestor locally with `python ingestor/test_reliable_feeds.py`
4. Check Supabase dashboard for database issues

## Success Metrics

After deployment, you should see:
- ✅ New posts appearing hourly on the website
- ✅ Content properly categorized into sections
- ✅ Tags working for filtering
- ✅ Search functionality working
- ✅ Archive system showing older posts
- ✅ No duplicate content (deduplication working)
- ✅ Content excerpts limited to 75 words
- ✅ All articles linking to source URLs

Congratulations! Your US Financial Moves platform is now live with automated news ingestion! 🎉
