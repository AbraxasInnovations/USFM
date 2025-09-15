import { Post } from '@/lib/supabase'
import TagChip from './TagChip'

interface FeaturedArticleProps {
  post: Post
}

export default function FeaturedArticle({ post }: FeaturedArticleProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <article className="featured-article">
      <div className="featured-image">
        <div className="placeholder-image">
          📈
        </div>
      </div>
      
      <div className="featured-content">
        <div className="featured-meta">
          <span className="category">{post.section_slug.toUpperCase()}</span>
          <span className="date">{formatDate(post.created_at)}</span>
        </div>
        
        <h1 className="featured-title">
          <a 
            href={post.source_url} 
            target="_blank" 
            rel="noopener nofollow ugc"
          >
            {post.title}
          </a>
        </h1>
        
        {post.summary && (
          <p className="featured-summary">{post.summary}</p>
        )}
        
        {post.excerpt && (
          <blockquote className="featured-excerpt">
            {post.excerpt}
          </blockquote>
        )}
        
        <div className="featured-footer">
          <span className="source">By {post.source_name}</span>
                      {post.tags && post.tags.length > 0 && (
                        <div className="featured-tags">
                          {post.tags.slice(0, 3).map((tag) => (
                            <TagChip key={tag} tag={tag} />
                          ))}
                        </div>
                      )}
        </div>
      </div>
    </article>
  )
}
