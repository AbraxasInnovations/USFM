import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import FeaturedArticle from '@/components/FeaturedArticle'
import TopHeadlines from '@/components/TopHeadlines'
import SectionNewsGrid from '@/components/SectionNewsGrid'
import Sidebar from '@/components/Sidebar'

// This function runs on the server
async function getPosts(): Promise<Post[]> {
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .order('created_at', { ascending: false })
    .limit(30) // Rolling window of 30 posts

  if (error) {
    console.error('Error fetching posts:', error)
    return []
  }

  return data || []
}

async function getSections(): Promise<Section[]> {
  const { data, error } = await supabase
    .from('sections')
    .select('*')
    .order('name')

  if (error) {
    console.error('Error fetching sections:', error)
    return []
  }

  return data || []
}

export default async function HomePage() {
  const [posts, sections] = await Promise.all([
    getPosts(),
    getSections()
  ])

  const featuredPost = posts[0]
  const topHeadlines = posts.slice(1, 7) // Next 6 posts for top headlines

  return (
    <>
      <Header sections={sections} />
      
      <main className="main">
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
          <SectionNewsGrid posts={posts} sections={sections} />

          {/* Additional Content Grid */}
          <section className="additional-content">
            <div className="market-sidebar">
              <Sidebar />
            </div>
          </section>
        </div>
      </main>
    </>
  )
}

// Enable ISR with 60 second revalidation
export const revalidate = 60
