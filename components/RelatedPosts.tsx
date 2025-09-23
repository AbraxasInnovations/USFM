import { Post } from '@/lib/supabase'
import Link from 'next/link'

interface RelatedPostsProps {
  currentPost: Post
  relatedPosts: Post[]
}

export default function RelatedPosts({ currentPost, relatedPosts }: RelatedPostsProps) {
  if (relatedPosts.length === 0) {
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
    <section className="related-posts mt-16 pt-8 border-t border-gray-200">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Articles</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {relatedPosts.map((post) => (
          <article key={post.id} className="related-post-card">
            <div className="related-post-content">
              <div className="related-post-meta mb-2">
                <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">
                  {post.section_slug}
                </span>
                <span className="text-xs text-gray-500 ml-2">
                  {formatDate(post.created_at)}
                </span>
              </div>
              
              <h3 className="related-post-title mb-2">
                <Link 
                  href={post.article_slug ? `/article/${post.article_slug}` : post.source_url}
                  className="text-gray-900 hover:text-blue-600 transition-colors"
                >
                  {post.title}
                </Link>
              </h3>
              
              {post.summary && (
                <p className="text-sm text-gray-600 line-clamp-3">
                  {post.summary}
                </p>
              )}
              
              <div className="related-post-footer mt-3">
                <span className="text-xs text-gray-500">
                  {post.source_name}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
