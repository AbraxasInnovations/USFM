import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import PostCard from '@/components/PostCard'
import { notFound } from 'next/navigation'

// This function runs on the server
async function getSectionPosts(slug: string): Promise<Post[]> {
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .eq('section_slug', slug)
    .order('created_at', { ascending: false })
    .limit(20)

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
    .order('slug')

  if (error) {
    console.error('Error fetching sections:', error)
    return []
  }

  return data || []
}

async function getSection(slug: string): Promise<Section | null> {
  const { data, error } = await supabase
    .from('sections')
    .select('*')
    .eq('slug', slug)
    .single()

  if (error) {
    console.error('Error fetching section:', error)
    return null
  }

  return data
}

interface SectionPageProps {
  params: Promise<{
    slug: string
  }>
}

export default async function SectionPage({ params }: SectionPageProps) {
  const resolvedParams = await params
  const [posts, sections, section] = await Promise.all([
    getSectionPosts(resolvedParams.slug),
    getSections(),
    getSection(resolvedParams.slug)
  ])

  if (!section) {
    notFound()
  }

  return (
    <>
      <Header sections={sections} />
      
      <main className="main">
        <div className="container">
          <div className="section-header">
            <h1 className="section-page-title">{section.name}</h1>
            <p className="section-description">
              Latest {section.name.toLowerCase()} news and updates
            </p>
          </div>

          <div className="section-posts-grid">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>

          {posts.length === 0 && (
            <div className="no-posts">
              <p>No posts found in this section yet.</p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

// Enable ISR with 60 second revalidation
export const revalidate = 60

// Generate static params for all sections
export async function generateStaticParams() {
  const sections = await getSections()
  
  return sections.map((section) => ({
    slug: section.slug,
  }))
}
