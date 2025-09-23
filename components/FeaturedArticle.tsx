import { Post } from '@/lib/supabase'
import TagChip from './TagChip'
import PostImage from './PostImage'

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
        <PostImage 
          imageUrl={post.image_url} 
          title={post.title}
          sectionSlug={post.section_slug}
          className="featured-image-content"
        />
      </div>
      
      <div className="featured-content">
        <div className="featured-meta">
          <span className="category">{post.section_slug.toUpperCase()}</span>
          <span className="date">{formatDate(post.created_at)}</span>
        </div>
        
        <h1 className="featured-title">
          <a 
            href={post.article_slug ? `/article/${post.article_slug}` : post.source_url} 
            target={post.article_slug ? "_self" : "_blank"} 
            rel={post.article_slug ? "" : "noopener nofollow ugc"}
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
