import { Post, Section } from '@/lib/supabase'

interface SectionNewsGridProps {
  posts: Post[]
  sections: Section[]
}

export default function SectionNewsGrid({ posts, sections }: SectionNewsGridProps) {
  // Filter out 'all' section and get posts for each section
  const sectionPosts = sections
    .filter(section => section.slug !== 'all')
    .map(section => ({
      section,
      posts: posts.filter(post => post.section_slug === section.slug).slice(0, 3)
    }))

  return (
    <div className="section-news-grid">
      {sectionPosts.map(({ section, posts: sectionPosts }) => (
        <div key={section.slug} className="section-row">
          <h2 className="section-title">{section.name}</h2>
          <div className="articles-grid">
            {sectionPosts.map((post) => (
              <article key={post.id} className="article-card">
                <div className="article-image">
                  <div className="placeholder-image">
                    📊
                  </div>
                </div>
                <div className="article-content">
                  <h3 className="article-title">
                    <a 
                      href={post.source_url} 
                      target="_blank" 
                      rel="noopener nofollow ugc"
                    >
                      {post.title}
                    </a>
                  </h3>
                  {post.summary && (
                    <p className="article-summary">{post.summary}</p>
                  )}
                  <div className="article-meta">
                    <span className="article-source">{post.source_name}</span>
                    <span className="article-date">
                      {new Date(post.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
