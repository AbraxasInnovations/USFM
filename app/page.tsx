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
  // Get all posts and sections directly from database
  const { data: allPosts, error: postsError } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .order('created_at', { ascending: false })
    .limit(100)

  const { data: sections, error: sectionsError } = await supabase
    .from('sections')
    .select('*')
    .order('name')

  if (postsError || sectionsError) {
    console.error('Error fetching data:', postsError || sectionsError)
    return { posts: [], sections: [], smartContent: {} }
  }

  // Implement Bloomberg prioritization logic
  const posts = allPosts || []
  const cutoffTime = new Date(Date.now() - 6 * 60 * 60 * 1000) // 6 hours ago

  // Separate Bloomberg posts from other posts
  const bloombergPosts = posts.filter(post => 
    post.source_name?.toLowerCase().includes('bloomberg')
  )

  const nonBloombergPosts = posts.filter(post => 
    !post.source_name?.toLowerCase().includes('bloomberg')
  )

  // Sort Bloomberg posts by date (most recent first)
  bloombergPosts.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  // Sort non-Bloomberg posts: scraped content first, then by created_at desc
  nonBloombergPosts.sort((a, b) => {
    // Prioritize scraped content
    if (a.scraped_content && !b.scraped_content) return -1
    if (!a.scraped_content && b.scraped_content) return 1
    
    // If both are scraped or both are not scraped, sort by date
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  // Create homepage content with Bloomberg prioritization:
  // 1. First post: Bloomberg (for featured article)
  // 2. Next posts: Diversified mix for top headlines
  let homepagePosts = []

  // Add Bloomberg post for featured article (if available)
  if (bloombergPosts.length > 0) {
    homepagePosts.push(bloombergPosts[0])
  }

  // Add remaining posts for the rest of homepage
  const remainingPosts = [...bloombergPosts.slice(1), ...nonBloombergPosts]
  homepagePosts = [...homepagePosts, ...remainingPosts]

  // Create smart content structure for sections
  const smartContent: any = {
    homepage: homepagePosts.slice(0, 30)
  }

  // Add section-specific content
  sections?.forEach(section => {
    const sectionPosts = posts.filter(post => post.section_slug === section.slug)
    smartContent[section.slug] = sectionPosts.slice(0, 5) // Limit to 5 posts per section
  })

  return { 
    posts: homepagePosts.slice(0, 30), 
    sections: sections || [], 
    smartContent 
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
