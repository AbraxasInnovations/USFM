import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import PostCard from '@/components/PostCard'
import { notFound } from 'next/navigation'

// This function runs on the server
async function getTagPosts(tag: string): Promise<Post[]> {
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .contains('tags', [tag])
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

interface TagPageProps {
  params: {
    tag: string
  }
}

export default async function TagPage({ params }: TagPageProps) {
  const [posts, sections] = await Promise.all([
    getTagPosts(params.tag),
    getSections()
  ])

  // If no posts found, show 404
  if (posts.length === 0) {
    notFound()
  }

  return (
    <>
      <Header sections={sections} />
      
      <main className="main">
        <div className="container">
          <div className="section-header">
            <h1 className="section-page-title">#{params.tag}</h1>
            <p className="section-description">
              Latest news tagged with #{params.tag}
            </p>
          </div>

          <div className="section-posts-grid">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        </div>
      </main>
    </>
  )
}

// Enable ISR with 60 second revalidation
export const revalidate = 60
