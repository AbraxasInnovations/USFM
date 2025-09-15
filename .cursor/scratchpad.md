# US Financial Moves - Finance Deal Feed Platform

## Background and Motivation
Transform the static finance news site into a comprehensive US Finance Deal Feed platform featuring:

**Core Concept:** Build a US Finance Deal Feed (M&A, LBO, take-privates, antitrust, major financings) with:
- Single source of truth in Supabase database
- Automated ingestion from multiple sources (SEC EDGAR, DOJ/FTC RSS, press releases)
- Fan-out delivery to website + optional X/Twitter
- Rolling window display (30 posts homepage, 20 per section)
- Server-side rendering with ISR for performance
- Search, filtering, and tag-based navigation

**Key Features:**
- Real-time deal feed with automated content ingestion
- Section-based navigation (M&A, LBO/PE, Regulatory, Capital Markets, etc.)
- Post structure with title, summary, quoted excerpts (≤75 words), source attribution
- Global search and tag-based filtering
- Archive system with pagination
- Content moderation controls
- Legal compliance (no full article text, proper attribution)

## Key Challenges and Analysis

**Technical Architecture:**
- Migrate from static HTML to Next.js App Router with ISR
- Set up Supabase database with proper schema and RLS policies
- Implement automated ingestion system using GitHub Actions + Python
- Build fan-out delivery system for web and social media
- Create server-side rendering with proper caching strategies

**Data Management:**
- Design normalized post structure with content deduplication
- Implement rolling window logic (30 homepage, 20 per section)
- Handle content transformation and excerpt limiting (≤75 words)
- Set up proper indexing for search and filtering

**Content Pipeline:**
- Build ingestor for SEC EDGAR, government RSS feeds, press releases
- Implement content normalization and deduplication
- Create delivery queue system for web revalidation and social posting
- Ensure legal compliance with publisher content usage

**User Experience:**
- Maintain clean, professional design while adding dynamic functionality
- Implement responsive search and filtering
- Create intuitive navigation between sections and tags
- Build archive system with proper pagination

## High-level Task Breakdown

### Phase 1: Database & Backend Setup
- [ ] Set up Supabase project and configure environment
- [ ] Create database schema (sections, posts, deliveries tables)
- [ ] Implement Row Level Security policies
- [ ] Set up database indexes for performance
- [ ] Create seed data for testing

### Phase 2: Next.js Migration & Core Features
- [ ] Migrate to Next.js App Router with TypeScript
- [ ] Implement ISR with 60s revalidation
- [ ] Create Supabase client configuration
- [ ] Build PostCard, SectionNav, TagChip components
- [ ] Implement homepage with rolling 30-post window
- [ ] Create section routes (/section/[slug]) with 20-post windows
- [ ] Build tag routes (/tag/[tag]) with filtering
- [ ] Implement archive system with pagination

### Phase 3: Search & Filtering
- [ ] Add global search functionality (server-side)
- [ ] Implement quick filters (All, Today, 3d, 7d)
- [ ] Create tag-based navigation and filtering
- [ ] Add search results page with proper SEO

### Phase 4: Content Ingestion System
- [ ] Build Python ingestor for SEC EDGAR data
- [ ] Add DOJ/FTC RSS feed processing
- [ ] Implement press release and IR page scraping
- [ ] Create content normalization and deduplication
- [ ] Set up GitHub Actions for automated ingestion
- [ ] Implement delivery queue system

### Phase 5: Fan-out & Delivery
- [ ] Create web revalidation API endpoint
- [ ] Build delivery worker for web updates
- [ ] Set up X/Twitter posting infrastructure (queued for v1)
- [ ] Implement error handling and retry logic

### Phase 6: Testing & Deployment
- [ ] Deploy to Vercel with proper environment variables
- [ ] Test with 35+ dummy posts to verify rolling windows
- [ ] Verify deduplication and content limits
- [ ] Test search and filtering functionality
- [ ] Implement monitoring and error tracking

## Project Status Board

### Completed (Static Site)
- [x] Set up project structure and package.json
- [x] Create basic HTML/CSS structure
- [x] Integrate Oswald font
- [x] Build main page layout
- [x] Add sample content
- [x] Test npm run dev

### Phase 1: Database & Backend Setup
- [x] Set up Supabase project
- [x] Create database schema
- [x] Configure RLS policies
- [x] Set up environment variables
- [x] Create seed data

### Phase 2: Next.js Migration ✅ COMPLETE
- [x] Install Next.js and dependencies
- [x] Migrate HTML/CSS to Next.js components
- [x] Set up App Router structure
- [x] Configure Supabase client
- [x] Implement ISR configuration

### Phase 3: Core Features ✅ COMPLETE
- [x] Build PostCard component
- [x] Create SectionNav component
- [x] Implement homepage rolling window
- [x] Build section routes
- [x] Create tag routes
- [x] Add archive system
- [x] Implement Morning Brew layout

### Phase 4: Search & Filtering ✅ COMPLETE
- [x] Implement global search
- [ ] Add quick filters (optional enhancement)
- [x] Create tag navigation
- [x] Build search results page

### Phase 5: Content Pipeline
- [ ] Build Python ingestor
- [ ] Set up GitHub Actions
- [ ] Create delivery system
- [ ] Implement error handling

### Phase 6: Testing & Deployment
- [ ] Deploy to Vercel
- [ ] Test with sample data
- [ ] Verify all functionality
- [ ] Set up monitoring

## Current Status / Progress Tracking

### ✅ COMPLETED (Static Site Phase)
- Created package.json with Vite development server
- Built complete HTML structure with finance news layout
- Integrated Oswald Medium 500 font from Google Fonts
- Implemented white-themed design with professional styling
- Added sample finance news content including:
  - Header with navigation
  - Hero section with main story
  - News grid with multiple articles
  - Sidebar with market data and trending topics
  - Responsive design for mobile devices
- Installed dependencies and started development server

### ✅ **PHASE 1, 2, 3, & 4 COMPLETE!** 
**CURRENT STATUS:** Full frontend platform with search and navigation successfully completed!

**✅ COMPLETED ACHIEVEMENTS:**
1. ✅ **Supabase project** configured with API keys
2. ✅ **Database schema** created (sections, posts, deliveries tables)
3. ✅ **Row Level Security** policies implemented
4. ✅ **Database indexes** set up for performance
5. ✅ **Seed data** created (40 sample posts for testing)
6. ✅ **Next.js migration** from Vite completed
7. ✅ **Database integration** working perfectly
8. ✅ **Rolling window** functionality confirmed (30 posts homepage)
9. ✅ **ISR with 60s revalidation** enabled
10. ✅ **Dynamic navigation** from database
11. ✅ **Post structure** with excerpts, tags, source attribution
12. ✅ **White theme and Oswald font** maintained
13. ✅ **Morning Brew layout** implemented with featured article + top headlines
14. ✅ **Section routes** (/section/[slug]) with 20-post windows
15. ✅ **Tag routes** (/tag/[tag]) with filtering
16. ✅ **Archive system** with pagination
17. ✅ **Global search** functionality (server-side PostgreSQL queries)
18. ✅ **Responsive design** for all components
19. ✅ **Article linking** - all articles link to source URLs with proper attribution

**🚀 READY FOR PHASE 5:** The frontend platform is complete. Ready to implement live news ingestion system.

### 📊 **SUPABASE IMPLEMENTATION STATUS**

**✅ COMPLETED DATABASE SETUP:**
- **Project Configuration:** Supabase project created with API keys configured
- **Database Schema:** Complete schema with 3 tables:
  - `sections` - Navigation taxonomy (All, M&A, LBO/PE, Regulatory, Capital Markets, Rumors)
  - `posts` - Main content table with all required fields (title, summary, excerpt, source, tags, etc.)
  - `deliveries` - Fan-out queue for web revalidation and social media posting
- **Security:** Row Level Security (RLS) policies implemented for anonymous read access
- **Performance:** Database indexes created for fast queries on section_slug, created_at, and tags
- **Data:** 40 sample posts seeded across all sections for testing

**✅ FRONTEND INTEGRATION:**
- **Real-time Data:** All pages now fetch live data from Supabase
- **Rolling Windows:** Homepage shows 30 most recent posts, sections show 20
- **Search:** Server-side PostgreSQL queries with ilike for title, summary, excerpt
- **ISR Caching:** 60-second revalidation keeps content fresh
- **Dynamic Navigation:** All sections and tags generated from database

### 🔄 **NEXT PHASE: LIVE NEWS INGESTION SYSTEM**

**CURRENT CHALLENGE:** All containers are currently populated with static seed data. We need to implement automated news ingestion to replace this with fresh, real-time financial news.

**PHASE 5 IMPLEMENTATION PLAN:**

#### 5.1 Content Sources & Ingestion
- **SEC EDGAR API:** 8-K filings, 10-K/10-Q reports for M&A and capital market activities
- **DOJ/FTC RSS Feeds:** Antitrust enforcement actions and merger reviews
- **Press Release Sources:** Company IR pages, PR Newswire, Business Wire
- **Financial News APIs:** Reuters, Bloomberg, Financial Times (if available)
- **Government Sources:** Federal Reserve announcements, Treasury Department releases

#### 5.2 Python Ingestor System
- **Content Fetching:** Automated scraping/API calls every 10 minutes
- **Content Normalization:** Transform raw data into standardized post format
- **Deduplication:** Use content_hash to prevent duplicate posts
- **Excerpt Limiting:** Enforce 75-word limit on quoted content
- **Tag Assignment:** Auto-generate relevant tags based on content analysis
- **Section Classification:** Route content to appropriate sections (M&A, LBO, etc.)

#### 5.3 GitHub Actions Automation
- **Cron Schedule:** Run ingestor every 10 minutes
- **Error Handling:** Retry logic with exponential backoff
- **Logging:** Comprehensive logging for monitoring and debugging
- **Environment Variables:** Secure API keys and database credentials

#### 5.4 Delivery & Revalidation System
- **Web Revalidation:** Call Next.js `/api/revalidate` endpoint after new posts
- **Social Media Queue:** Prepare X/Twitter posts (held until API enabled)
- **Error Recovery:** Failed deliveries retry with backoff
- **Monitoring:** Track ingestion success rates and content quality

#### 5.5 Content Quality & Legal Compliance
- **Publisher Terms:** Respect content usage policies (title, URL, ≤75-word quotes)
- **Attribution:** Clear source credit and "noopener nofollow ugc" links
- **Content Filtering:** Remove or flag inappropriate content
- **Manual Review:** Admin tools for content moderation

**IMMEDIATE NEXT STEPS:**
1. **Research Content Sources:** Identify reliable APIs and RSS feeds for financial news
2. **Build Python Ingestor:** Create modular ingestion system for different source types
3. **Set up GitHub Actions:** Configure automated scheduling and deployment
4. **Test with Real Data:** Validate ingestion with actual financial news sources
5. **Deploy to Production:** Replace seed data with live news feeds

### 🎨 **NEW DESIGN REQUIREMENT: Morning Brew Style Layout**
**User Request:** Implement Morning Brew style layout with:
- **Left side:** One big featured article with picture
- **Right side:** Top 10 most popular headlines with links to full articles
- **Note for future:** When implementing live news pulls, replace top section articles and update with proper links to full article pages

### 📐 **UPDATED LAYOUT REQUIREMENTS:**
**User Request:** Refine the Morning Brew layout with:
- **Top Headlines Height:** Make right sidebar same height as left featured article
- **Container Width:** Make both containers same width (equal columns)
- **Reduce Headlines:** Remove some headline spaces to fit height constraint
- **Section News Grid:** Add rows below the top section with:
  - **3 articles per row** for each navigation topic (M&A, LBO/PE, Regulatory, Capital Markets, Rumors)
  - **Layout:** Picture at top, description at bottom for each article
  - **Grid continues** all the way to bottom of page
- **CRITICAL LINKING REQUIREMENT:** ALL articles must link to their respective full article pages - this is the core functionality of a news website
- **Future Integration:** When live news pulls are implemented, all predetermined spots must populate with real articles that link to their full content

## Executor's Feedback or Assistance Requests

### 🎯 **PHASE 5: LIVE NEWS INGESTION SYSTEM**

**STATUS:** Frontend platform complete! Ready to implement automated news ingestion.

**CURRENT ACHIEVEMENT:**
✅ **Complete Frontend Platform** - All user-facing features are working:
- Morning Brew layout with featured article + top headlines
- Section-based navigation (M&A, LBO/PE, Regulatory, Capital Markets, Rumors)
- Tag-based filtering and search functionality
- Archive system with pagination
- Responsive design with proper article linking
- Real-time data from Supabase database

**NEXT CRITICAL PHASE:**
🔄 **Live News Ingestion System** - Replace static seed data with real-time financial news

**IMMEDIATE ASSISTANCE NEEDED:**
1. **Content Source Research:** Identify reliable APIs and RSS feeds for:
   - SEC EDGAR filings (8-K, 10-K, 10-Q)
   - DOJ/FTC antitrust enforcement
   - Company press releases and IR pages
   - Financial news APIs (Reuters, Bloomberg, etc.)

2. **Python Ingestor Development:** Build modular system for:
   - Automated content fetching every 10 minutes
   - Content normalization and deduplication
   - Section classification and tag assignment
   - Legal compliance (≤75-word excerpts, proper attribution)

3. **GitHub Actions Setup:** Configure automated scheduling and deployment

4. **API Revalidation Endpoint:** Create `/api/revalidate` for web updates

**READY TO EXECUTE:** The foundation is solid. Ready to build the content ingestion pipeline that will populate all containers with fresh, real-time financial news.

## Lessons
- Include info useful for debugging in the program output
- Read the file before you try to edit it
- If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
- Always ask before using the -force git command
