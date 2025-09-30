import { supabase } from '@/lib/supabase'
import Header from '@/components/Header'
import RelatedPosts from '@/components/RelatedPosts'
import { notFound } from 'next/navigation'
import { Metadata } from 'next'
import Image from 'next/image'

interface ArticlePageProps {
  params: Promise<{ slug: string }>
}

async function getArticle(slug: string) {
  const { data: posts, error } = await supabase
    .from('posts')
    .select('*')
    .eq('article_slug', slug)
    .eq('status', 'published')
    .order('created_at', { ascending: false })

  if (error || !posts || posts.length === 0) {
    return null
  }

  // Return the most recent article (first in the ordered list)
  return posts[0]
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

export async function generateMetadata({ params }: ArticlePageProps): Promise<Metadata> {
  const { slug } = await params
  const article = await getArticle(slug)

  if (!article) {
    return {
      title: 'Article Not Found | US Finance Moves',
    }
  }

  const title = `${article.title} | US Finance Moves`
  const description = article.summary || article.excerpt || article.title
  const canonicalUrl = `https://www.usfinancemoves.com/article/${article.article_slug}`
  const imageUrl = article.image_url || 'https://www.usfinancemoves.com/og-default.jpg'

  return {
    title,
    description: description.length > 160 ? description.substring(0, 157) + '...' : description,
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title,
      description,
      url: canonicalUrl,
      siteName: 'US Finance Moves',
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: article.title,
        },
      ],
      locale: 'en_US',
      type: 'article',
      publishedTime: article.created_at,
      modifiedTime: article.updated_at || article.created_at,
      authors: [article.source_name || 'USFM'],
      section: article.section_slug || 'Finance',
      tags: article.tags || [],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
      creator: '@usfinancemoves',
    },
  }
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

  // Generate JSON-LD schema
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": article.title,
    "description": article.summary || article.excerpt || article.title,
    "datePublished": article.created_at,
    "dateModified": article.updated_at || article.created_at,
    "author": {
      "@type": "Person",
      "name": article.source_name || "USFM",
      "url": "https://derekpethel.com/press"
    },
    "publisher": {
      "@type": "Organization",
      "name": "US Finance Moves",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.usfinancemoves.com/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": `https://www.usfinancemoves.com/article/${article.article_slug}`
    },
    "image": article.image_url ? [article.image_url] : [],
    "articleSection": article.section_slug || "Finance",
    "keywords": article.tags ? article.tags.join(", ") : "",
    "url": `https://www.usfinancemoves.com/article/${article.article_slug}`
  }

  return (
    <>
      {/* JSON-LD Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      
      <div className="min-h-screen bg-white">
        <Header sections={sections} />
      
      <main className="container mx-auto px-4 py-8">
        <article className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8 md:p-12">
            {/* Article Header - Newsletter Style */}
            <header className="mb-16">
            
            {/* Thumbnail Image for SEC Articles - Centered with More Space */}
            {article.image_url && (
              <div className="flex justify-center items-center" style={{ marginTop: '3rem', marginBottom: '4rem', width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
                  <Image 
                    src={article.image_url} 
                    alt={article.title}
                    width={800}
                    height={400}
                    className="h-64 md:h-80 object-cover rounded-lg shadow-lg"
                    style={{ 
                      maxWidth: '800px', 
                      width: '100%',
                      display: 'block',
                      margin: '0 auto'
                    }}
                    priority
                    sizes="(max-width: 768px) 100vw, 800px"
                  />
                </div>
              </div>
            )}
            
            <h1 className="text-3xl md:text-5xl font-extrabold text-black mb-8 leading-tight text-center" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif', letterSpacing: '-0.02em', marginTop: '4rem' }}>
              {article.title}
            </h1>
            
            <div className="flex items-center justify-center text-gray-600 text-base mb-8">
              <span className="font-medium">By {article.source_name}</span>
              <span className="mx-3">•</span>
              <span>{formatDate(article.created_at)}</span>
            </div>
            
            {article.summary && (
              <div className="bg-gray-50 border-l-4 border-blue-500 p-8 mb-12 rounded-r-lg" style={{ marginTop: '2rem' }}>
                <p className="text-lg text-gray-800 leading-relaxed font-medium">
                  {article.summary}
                </p>
              </div>
            )}
          </header>

          {/* Article Content - Newsletter Style Typography */}
          {article.scraped_content && (
            <div className="article-content mb-20" style={{ marginTop: '2rem' }}>
              <div 
                className="prose prose-lg max-w-none text-gray-800 leading-relaxed"
                style={{
                  fontFamily: 'Georgia, "Times New Roman", serif',
                  lineHeight: '1.8',
                  fontSize: '18px'
                }}
                dangerouslySetInnerHTML={{ 
                  __html: article.scraped_content
                    .replace(/\n\n/g, '</p><p class="mb-10 text-gray-800 leading-relaxed" style="font-size: 18px; line-height: 1.8;">')
                    .replace(/^/, '<p class="mb-10 text-gray-800 leading-relaxed" style="font-size: 18px; line-height: 1.8;">')
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
    </>
  )
}

export const revalidate = 60
