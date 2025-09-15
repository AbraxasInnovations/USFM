import { Post } from '@/lib/supabase'
import TagChip from './TagChip'

interface PostCardProps {
  post: Post
}

export default function PostCard({ post }: PostCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <article className="news-card">
      <div className="news-content">
        <span className="category">{post.section_slug.toUpperCase()}</span>
        <h3>
          <a 
            href={post.source_url} 
            target="_blank" 
            rel="noopener nofollow ugc"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            {post.title}
          </a>
        </h3>
        {post.summary && (
          <p>{post.summary}</p>
        )}
        {post.excerpt && (
          <blockquote style={{ 
            margin: '1rem 0', 
            padding: '1rem', 
            borderLeft: '4px solid #e5e5e5',
            backgroundColor: '#f8f9fa',
            fontStyle: 'italic'
          }}>
            {post.excerpt}
          </blockquote>
        )}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '1rem' }}>
          <span className="timestamp">
            {post.source_name} • {formatDate(post.created_at)}
          </span>
        </div>
        {post.tags && post.tags.length > 0 && (
          <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {post.tags.map((tag) => (
              <TagChip key={tag} tag={tag} />
            ))}
          </div>
        )}
      </div>
    </article>
  )
}
