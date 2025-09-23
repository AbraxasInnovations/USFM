# Twitter/X Integration Setup Guide

## 🐦 Overview

This guide will help you set up automated Twitter/X posting for your US Financial Moves articles with proper rate limiting to stay within the free tier limits.

## 📋 Prerequisites

1. **Twitter Developer Account** (Free tier)
2. **Twitter App** with API v2 access
3. **Bearer Token** for authentication

## 🔧 Step 1: Twitter Developer Setup

### 1.1 Create Twitter Developer Account
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for a developer account (free)
3. Complete the application process

### 1.2 Create a Twitter App
1. Go to [developer.twitter.com/en/portal/dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click "Create App"
3. Fill in app details:
   - **App Name**: "US Financial Moves"
   - **Description**: "Automated financial news posting"
   - **Website**: Your website URL
   - **Callback URL**: Leave blank

### 1.3 Get Your Bearer Token
1. In your app dashboard, go to "Keys and Tokens"
2. Copy your **Bearer Token** (starts with `AAAAAAAAAAAAAAAAAAAAA...`)
3. **Keep this secret!** Don't share it publicly

## 🔐 Step 2: Environment Configuration

### 2.1 Add to GitHub Secrets
Add these secrets to your GitHub repository:

```
X_ENABLED=true
X_BEARER=your_bearer_token_here
```

### 2.2 Add to Local Environment
Add to your `.env.local` file:

```
X_ENABLED=true
X_BEARER=your_bearer_token_here
```

## 🧪 Step 3: Test the Integration

### 3.1 Test Twitter Connection
```bash
cd ingestor
python test_twitter.py
```

This will test:
- ✅ Twitter API connection
- ✅ Tweet creation
- ✅ Delivery manager formatting

### 3.2 Expected Output
```
✅ Twitter API connection successful!
✅ Test tweet created successfully! Tweet ID: 1234567890
🎉 Twitter integration is ready!
```

## 📊 Step 4: Rate Limiting Configuration

### 4.1 Free Tier Limits
- **300 tweets per 15 minutes**
- **10 tweets per hour** (conservative setting)

### 4.2 Current Settings
The system is configured with:
- **10 posts per hour** maximum
- **Automatic rate limit detection**
- **Graceful fallback** when limits are reached

## 🚀 Step 5: Deploy the Delivery Worker

### 5.1 GitHub Actions
The delivery worker runs automatically every 10 minutes via GitHub Actions:
- **File**: `.github/workflows/delivery-worker.yml`
- **Schedule**: Every 10 minutes
- **Manual trigger**: Available in GitHub Actions tab

### 5.2 How It Works
1. **News Ingestor** creates articles and queues Twitter posts
2. **Delivery Worker** processes queued posts every 10 minutes
3. **Rate Limiting** ensures you stay within free tier limits
4. **Error Handling** retries failed posts up to 5 times

## 📝 Step 6: Tweet Format

### 6.1 Tweet Structure
```
📈 [Article Title]

[Summary if short enough]

#SECTION #M&A #Crypto

[Source URL]
```

### 6.2 Example Tweet
```
📈 First Community Corporation to Acquire Signature Bank of Georgia in Strategic Merger

The $32.4 million deal represents a significant expansion in the Georgia banking market.

#MA #SEC #BANKING

https://example.com/article
```

## 🔍 Step 7: Monitoring

### 7.1 Check Delivery Status
Monitor your deliveries in the Supabase `deliveries` table:
```sql
SELECT * FROM deliveries 
WHERE channel = 'x' 
ORDER BY created_at DESC 
LIMIT 10;
```

### 7.2 GitHub Actions Logs
Check the delivery worker logs in:
- **GitHub Actions** → **Delivery Worker** → **View logs**

### 7.3 Rate Limit Monitoring
The system logs rate limit status:
```
Rate limit reached. Reset in 900 seconds
Hourly limit reached (10 posts/hour)
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Twitter API connection failed"
- ✅ Check your Bearer Token
- ✅ Verify X_ENABLED=true
- ✅ Ensure your Twitter app has API v2 access

#### 2. "Rate limit exceeded"
- ✅ This is normal - the system will retry later
- ✅ Check your posting frequency
- ✅ Consider upgrading to paid Twitter API

#### 3. "Delivery failed after 5 attempts"
- ✅ Check Twitter API status
- ✅ Verify your app permissions
- ✅ Review the error logs

### Debug Commands
```bash
# Test connection only
python -c "from ingestor.twitter_client import TwitterClient; from ingestor.config import X_BEARER; client = TwitterClient(X_BEARER); print('✅ Connected' if client.test_connection() else '❌ Failed')"

# Check rate limits
python -c "from ingestor.twitter_client import TwitterClient; from ingestor.config import X_BEARER; client = TwitterClient(X_BEARER); print(f'Remaining: {client.rate_limits[\"tweets\"][\"remaining\"]}')"
```

## 📈 Next Steps

1. **Monitor Performance**: Watch your tweet engagement
2. **Optimize Timing**: Adjust posting frequency based on engagement
3. **Content Quality**: Ensure articles are high-quality and relevant
4. **Scale Up**: Consider paid Twitter API for higher limits

## 🎯 Success Metrics

- **Posts per day**: 10-20 (within free tier)
- **Engagement rate**: Monitor likes, retweets, clicks
- **Error rate**: Should be <5% under normal conditions

---

**Need Help?** Check the logs in GitHub Actions or run the test script for diagnostics.
