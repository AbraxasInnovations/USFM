import { Post } from '@/lib/supabase'
import Link from 'next/link'

interface ScrapedArticlesSectionProps {
  posts: Post[]
}

export default function ScrapedArticlesSection({ posts }: ScrapedArticlesSectionProps) {
  // Filter posts that have scraped content
  const scrapedPosts = posts.filter(post => post.scraped_content && post.article_slug)
  
  if (scrapedPosts.length === 0) {
    return null
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <section className="scraped-articles-section">
      <div className="section-header">
        <h2 className="section-title">📰 Written Articles</h2>
        <p className="section-description">
          In-house articles for detailed analysis of US financial moves
        </p>
      </div>
      
      <div className="scraped-articles-grid">
        {scrapedPosts.slice(0, 3).map((post) => (
          <article key={post.id} className="scraped-article-card">
            <div className="scraped-article-content">
              <div className="scraped-article-meta">
                <span className="scraped-article-category">{post.section_slug.toUpperCase()}</span>
                <span className="scraped-article-date">{formatDate(post.created_at)}</span>
              </div>
              
              <h3 className="scraped-article-title">
                <Link href={`/article/${post.article_slug}`}>
                  {post.title}
                </Link>
              </h3>
              
              {post.summary && (
                <p className="scraped-article-summary">{post.summary}</p>
              )}
              
              <div className="scraped-article-footer">
                <span className="scraped-article-source">By {post.source_name}</span>
                <Link 
                  href={`/article/${post.article_slug}`}
                  className="scraped-article-link"
                >
                  Read Full Article →
                </Link>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
