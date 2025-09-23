import { supabase } from '@/lib/supabase'
import Header from '@/components/Header'
import RelatedPosts from '@/components/RelatedPosts'
import { notFound } from 'next/navigation'

interface ArticlePageProps {
  params: Promise<{ slug: string }>
}

async function getArticle(slug: string) {
  const { data: post, error } = await supabase
    .from('posts')
    .select('*')
    .eq('article_slug', slug)
    .eq('status', 'published')
    .single()

  if (error || !post) {
    return null
  }

  return post
}

async function getSections() {
  const { data: sections, error } = await supabase
    .from('sections')
    .select('*')
    .order('created_at')

  if (error) {
    return []
  }

  return sections
}

async function getRelatedPosts(currentPost: any, limit: number = 6) {
  try {
    // Extract keywords from title and tags
    const titleWords = currentPost.title.toLowerCase().split(/\s+/).filter((word: string) => word.length > 3)
    const tagWords = currentPost.tags || []
    const allKeywords = [...titleWords, ...tagWords]
    
    // Create search terms for better matching
    const searchTerms = allKeywords.slice(0, 5) // Use top 5 keywords
    
    // Build a complex query to find related posts
    let query = supabase
      .from('posts')
      .select('*')
      .eq('status', 'published')
      .neq('id', currentPost.id) // Exclude current post
      .limit(limit)
    
    // Try to find posts with matching tags first
    if (tagWords.length > 0) {
      const { data: tagMatches } = await supabase
        .from('posts')
        .select('*')
        .eq('status', 'published')
        .neq('id', currentPost.id)
        .overlaps('tags', tagWords)
        .limit(limit)
      
      if (tagMatches && tagMatches.length > 0) {
        return tagMatches
      }
    }
    
    // Fallback: find posts in the same section
    const { data: sectionMatches } = await supabase
      .from('posts')
      .select('*')
      .eq('status', 'published')
      .eq('section_slug', currentPost.section_slug)
      .neq('id', currentPost.id)
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (sectionMatches && sectionMatches.length > 0) {
      return sectionMatches
    }
    
    // Final fallback: get recent posts
    const { data: recentPosts } = await supabase
      .from('posts')
      .select('*')
      .eq('status', 'published')
      .neq('id', currentPost.id)
      .order('created_at', { ascending: false })
      .limit(limit)
    
    return recentPosts || []
    
  } catch (error) {
    console.error('Error fetching related posts:', error)
    return []
  }
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { slug } = await params
  const [article, sections] = await Promise.all([
    getArticle(slug),
    getSections()
  ])

  if (!article) {
    notFound()
  }

  // Get related posts
  const relatedPosts = await getRelatedPosts(article, 6)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <div className="min-h-screen bg-[#fefefe]">
      <Header sections={sections} />
      
      <main className="container mx-auto px-4 py-12">
        <article className="max-w-4xl mx-auto">
          {/* Article Header - More Spacious */}
          <header className="mb-12">
            <div className="mb-6">
              <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-4 py-2 rounded-full">
                {article.section_slug.toUpperCase()}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              {article.title}
            </h1>
            
            <div className="flex items-center text-gray-600 text-base mb-8">
              <span className="font-medium">By {article.source_name}</span>
              <span className="mx-3">•</span>
              <span>{formatDate(article.created_at)}</span>
            </div>
            
            {article.summary && (
              <div className="bg-gray-50 border-l-4 border-blue-500 p-6 mb-8">
                <p className="text-xl text-gray-800 leading-relaxed font-medium">
                  {article.summary}
                </p>
              </div>
            )}
          </header>

          {/* Article Content - Better Typography */}
          {article.scraped_content && (
            <div className="article-content mb-16">
              <div 
                className="text-gray-800 leading-relaxed text-lg space-y-6"
                dangerouslySetInnerHTML={{ 
                  __html: article.scraped_content
                    .replace(/\n\n/g, '</p><p class="mb-6">')
                    .replace(/^/, '<p class="mb-6">')
                    .replace(/$/, '</p>')
                }}
              />
            </div>
          )}

          {/* Article Footer */}
          <footer className="mt-16 pt-8 border-t border-gray-200">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-2">
                  Originally published by {article.source_name}
                </p>
                <a 
                  href={article.source_url}
                  target="_blank"
                  rel="noopener nofollow ugc"
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View original article →
                </a>
              </div>
              
              {article.tags && article.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {article.tags.map((tag: string) => (
                    <span 
                      key={tag}
                      className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </footer>

          {/* Related Posts Section */}
          <RelatedPosts currentPost={article} relatedPosts={relatedPosts} />
        </article>
      </main>
    </div>
  )
}

export const revalidate = 60
