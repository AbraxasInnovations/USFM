import { Post } from '@/lib/supabase'

interface TopHeadlinesProps {
  posts: Post[]
}

export default function TopHeadlines({ posts }: TopHeadlinesProps) {
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="top-headlines">
      <h3 className="headlines-title">Top Headlines</h3>
      <div className="headlines-list">
        {posts.slice(0, 8).map((post, index) => (
          <div key={post.id} className="headline-item">
            <div className="headline-number">{index + 1}</div>
            <div className="headline-content">
              <h4 className="headline-title">
                <a 
                  href={post.article_slug ? `/article/${post.article_slug}` : post.source_url} 
                  target={post.article_slug ? "_self" : "_blank"} 
                  rel={post.article_slug ? "" : "noopener nofollow ugc"}
                >
                  {post.title}
                </a>
              </h4>
              <div className="headline-meta">
                <span className="headline-source">{post.source_name}</span>
                <span className="headline-separator"> | </span>
                <span className="headline-time">{formatTime(post.created_at)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
