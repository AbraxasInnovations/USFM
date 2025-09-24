import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import FeaturedArticle from '@/components/FeaturedArticle'
import TopHeadlines from '@/components/TopHeadlines'
import SectionNewsGrid from '@/components/SectionNewsGrid'
import ScrapedArticlesSection from '@/components/ScrapedArticlesSection'
import Sidebar from '@/components/Sidebar'
import AdSense from '@/components/AdSense'

// This function runs on the server
async function getSmartContent(): Promise<{ posts: Post[], sections: Section[], smartContent: any }> {
  try {
    // Fetch smart content from our API
    const baseUrl = process.env.VERCEL_URL 
      ? `https://${process.env.VERCEL_URL}` 
      : 'http://localhost:3000'
    
    const response = await fetch(`${baseUrl}/api/smart-content`, {
      next: { revalidate: 60 } // Use ISR with 60 second revalidation
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch smart content')
    }
    
    const { smartContent } = await response.json()
    
    // Get sections
    const { data: sections, error: sectionsError } = await supabase
      .from('sections')
      .select('*')
      .order('name')

    if (sectionsError) {
      console.error('Error fetching sections:', sectionsError)
      return { posts: [], sections: [], smartContent: {} }
    }

    // Get homepage posts from smart content
    const posts = smartContent.homepage || []
    
    return { posts, sections: sections || [], smartContent }
    
  } catch (error) {
    console.error('Error fetching smart content:', error)
    
    // Fallback to regular posts if smart content fails
    const { data: posts, error: postsError } = await supabase
      .from('posts')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
      .limit(30)

    const { data: sections, error: sectionsError } = await supabase
      .from('sections')
      .select('*')
      .order('name')

    return { 
      posts: posts || [], 
      sections: sections || [], 
      smartContent: { homepage: posts || [] }
    }
  }
}

export default async function HomePage() {
  const { posts, sections, smartContent } = await getSmartContent()

  const featuredPost = posts[0]
  const topHeadlines = posts.slice(1, 7) // Next 6 posts for top headlines

  return (
    <>
      <Header sections={sections} />
      
      <main className="main">
        <div className="desktop-layout">
          {/* Left Ad Container - Desktop Only */}
          <div className="ad-container ad-left">
            <div className="ad-slot">
              <AdSense
                adClient="ca-pub-XXXXXXXXXXXXXXXX"
                adSlot="XXXXXXXXXX"
                adFormat="auto"
                fullWidthResponsive={false}
                style={{ display: 'block', width: '100%', maxWidth: '300px' }}
              />
            </div>
          </div>

          {/* Main Content Container */}
          <div className="main-content">
            <div className="container">
              {/* Morning Brew Style Layout */}
              <section className="morning-brew-layout">
                <div className="featured-section">
                  {featuredPost && (
                    <FeaturedArticle post={featuredPost} />
                  )}
                </div>
                
                <div className="headlines-section">
                  <TopHeadlines posts={topHeadlines} />
                </div>
              </section>

              {/* Section News Grid */}
              <SectionNewsGrid posts={posts} sections={sections} smartContent={smartContent} />

              {/* Scraped Articles Section */}
              <ScrapedArticlesSection posts={posts} />

              {/* Additional Content Grid */}
              <section className="additional-content">
                <div className="market-sidebar">
                  <Sidebar />
                </div>
              </section>
            </div>
          </div>

          {/* Right Ad Container - Desktop Only */}
          <div className="ad-container ad-right">
            <div className="ad-slot">
              <AdSense
                adClient="ca-pub-XXXXXXXXXXXXXXXX"
                adSlot="XXXXXXXXXX"
                adFormat="auto"
                fullWidthResponsive={false}
                style={{ display: 'block', width: '100%', maxWidth: '300px' }}
              />
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

// Enable ISR with 60 second revalidation
export const revalidate = 60
