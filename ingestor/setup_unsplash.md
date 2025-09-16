# Unsplash API Setup

To enable automatic image search, you need to get a free Unsplash API key:

## Step 1: Create Unsplash Account
1. Go to [https://unsplash.com/developers](https://unsplash.com/developers)
2. Click "Register as a developer"
3. Sign up for a free account

## Step 2: Create New Application
1. Click "Your apps" in the top navigation
2. Click "New Application"
3. Fill out the form:
   - **Application name:** US Financial Moves
   - **Description:** News aggregator for financial content
   - **Website URL:** https://usfinancemoves.com
4. Accept the API Use and Guidelines
5. Click "Create application"

## Step 3: Get Access Key
1. Your new app will be created
2. Copy the "Access Key" (starts with something like `abc123...`)
3. Add it to your GitHub Secrets as `UNSPLASH_ACCESS_KEY`

## Step 4: Add to GitHub Secrets
1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `UNSPLASH_ACCESS_KEY`
5. Value: Your access key from Step 3
6. Click "Add secret"

## Free Tier Limits
- 50 requests per hour
- 5,000 requests per month
- Perfect for your hourly news ingestion!

## How It Works
The system will:
1. Try to use images from RSS feeds first (MarketWatch)
2. If no image, search Unsplash based on headline keywords
3. If search fails, use a fallback image based on section type
4. All images are high-quality and relevant to financial content
