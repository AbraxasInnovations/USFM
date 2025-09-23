import { Post, Section } from '@/lib/supabase'
import PostImage from './PostImage'

interface SectionNewsGridProps {
  posts: Post[]
  sections: Section[]
  smartContent?: any
}

export default function SectionNewsGrid({ posts, sections, smartContent }: SectionNewsGridProps) {
  // Use smart content if available, otherwise fallback to regular filtering
  const sectionPosts = sections
    .filter(section => section.slug !== 'all')
    .map(section => {
      let sectionPosts = []
      
      if (smartContent && smartContent[section.slug]) {
        // Use smart content for this section
        sectionPosts = smartContent[section.slug].slice(0, 3)
      } else {
        // Fallback to regular filtering
        sectionPosts = posts.filter(post => post.section_slug === section.slug).slice(0, 3)
      }
      
      return {
        section,
        posts: sectionPosts
      }
    })

  return (
    <div className="section-news-grid">
      {sectionPosts.map(({ section, posts: sectionPosts }) => (
        <div key={section.slug} className="section-row">
          <h2 className="section-title">{section.name}</h2>
          <div className="articles-grid">
            {sectionPosts.map((post: Post) => (
              <article key={post.id} className="article-card">
                <div className="article-image">
                  <PostImage 
                    imageUrl={post.image_url} 
                    title={post.title}
                    sectionSlug={post.section_slug}
                    className="article-image-content"
                  />
                </div>
                <div className="article-content">
                  <h3 className="article-title">
                    <a 
                      href={post.article_slug ? `/article/${post.article_slug}` : post.source_url} 
                      target={post.article_slug ? "_self" : "_blank"} 
                      rel={post.article_slug ? "" : "noopener nofollow ugc"}
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
