import { supabase } from '@/lib/supabase'
import { Post, Section } from '@/lib/supabase'
import Header from '@/components/Header'
import PostCard from '@/components/PostCard'
import Sidebar from '@/components/Sidebar'

interface SearchPageProps {
  searchParams: Promise<{
    q?: string
    page?: string
    limit?: string
  }>
}

const POSTS_PER_PAGE = 20

// Fetch posts based on search query
async function getSearchPosts(query: string, page: number, limit: number): Promise<{ posts: Post[], totalCount: number }> {
  const offset = (page - 1) * limit

  // Use PostgreSQL full-text search with multiple fields
  const { data, error, count } = await supabase
    .from('posts')
    .select('*', { count: 'exact' })
    .eq('status', 'published')
    .or(`title.ilike.%${query}%,summary.ilike.%${query}%,excerpt.ilike.%${query}%`)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) {
    console.error('Error fetching search posts:', error)
    return { posts: [], totalCount: 0 }
  }
  return { posts: data || [], totalCount: count || 0 }
}

// Fetch all sections for navigation
async function getSections(): Promise<Section[]> {
  const { data, error } = await supabase
    .from('sections')
    .select('*')
    .order('created_at', { ascending: true })

  if (error) {
    console.error('Error fetching sections:', error)
    return []
  }
  return data || []
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const resolvedSearchParams = await searchParams
  const query = resolvedSearchParams.q || ''
  const currentPage = parseInt(resolvedSearchParams.page || '1', 10)
  const limit = parseInt(resolvedSearchParams.limit || String(POSTS_PER_PAGE), 10)

  const { posts, totalCount } = await getSearchPosts(query, currentPage, limit)
  const sections = await getSections()

  const totalPages = Math.ceil(totalCount / limit)
  const hasNextPage = currentPage < totalPages
  const hasPreviousPage = currentPage > 1

  return (
    <>
      <Header sections={sections} />

      <main className="main">
        <div className="container">
          <div className="section-header">
            <h1 className="section-page-title">
              {query ? `Search Results for "${query}"` : 'Search'}
            </h1>
            <p className="section-description">
              {query 
                ? `Found ${totalCount} result${totalCount !== 1 ? 's' : ''} for "${query}"`
                : 'Enter a search term to find relevant financial news and deals.'
              }
            </p>
          </div>

          {/* Search Form */}
          <div className="search-form">
            <form method="GET" action="/search">
              <div className="search-input-group">
                <input
                  type="text"
                  name="q"
                  placeholder="Search for deals, companies, or topics..."
                  defaultValue={query}
                  className="search-input"
                />
                <button type="submit" className="search-button">
                  Search
                </button>
              </div>
            </form>
          </div>

          {query && posts.length > 0 ? (
            <>
              <div className="section-posts-grid">
                {posts.map((post) => (
                  <PostCard key={post.id} post={post} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  {hasPreviousPage && (
                    <a
                      href={`/search?q=${encodeURIComponent(query)}&page=${currentPage - 1}&limit=${limit}`}
                      className="pagination-button prev"
                    >
                      Previous Page
                    </a>
                  )}
                  <span className="pagination-info">
                    Page {currentPage} of {totalPages}
                  </span>
                  {hasNextPage && (
                    <a
                      href={`/search?q=${encodeURIComponent(query)}&page=${currentPage + 1}&limit=${limit}`}
                      className="pagination-button"
                    >
                      Next Page
                    </a>
                  )}
                </div>
              )}
            </>
          ) : query ? (
            <p className="no-posts">No results found for "{query}". Try different keywords.</p>
          ) : null}

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

export const revalidate = 60
