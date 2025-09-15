import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import PostCard from '@/components/PostCard'
import Link from 'next/link'

// This function runs on the server
async function getArchivePosts(page: number = 1, limit: number = 20): Promise<{ posts: Post[], hasMore: boolean }> {
  const offset = (page - 1) * limit
  
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) {
    console.error('Error fetching posts:', error)
    return { posts: [], hasMore: false }
  }

  // Check if there are more posts
  const { count } = await supabase
    .from('posts')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'published')
    .gt('created_at', data?.[data.length - 1]?.created_at || '1900-01-01')

  return { 
    posts: data || [], 
    hasMore: (count || 0) > 0 
  }
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

interface ArchivePageProps {
  searchParams: Promise<{
    page?: string
  }>
}

export default async function ArchivePage({ searchParams }: ArchivePageProps) {
  const resolvedSearchParams = await searchParams
  const page = parseInt(resolvedSearchParams.page || '1', 10)
  const [archiveData, sections] = await Promise.all([
    getArchivePosts(page),
    getSections()
  ])

  const { posts, hasMore } = archiveData

  return (
    <>
      <Header sections={sections} />
      
      <main className="main">
        <div className="container">
          <div className="section-header">
            <h1 className="section-page-title">Archive</h1>
            <p className="section-description">
              Browse all published articles from our finance deal feed
            </p>
          </div>

          <div className="section-posts-grid">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>

          {posts.length === 0 && (
            <div className="no-posts">
              <p>No posts found in the archive.</p>
            </div>
          )}

          {/* Pagination */}
          <div className="pagination">
            {page > 1 && (
              <Link 
                href={`/archive?page=${page - 1}`}
                className="pagination-button prev"
              >
                ← Previous Page
              </Link>
            )}
            
            <span className="pagination-info">
              Page {page}
            </span>
            
            {hasMore && (
              <Link 
                href={`/archive?page=${page + 1}`}
                className="pagination-button next"
              >
                Next Page →
              </Link>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

// Enable ISR with 60 second revalidation
export const revalidate = 60
