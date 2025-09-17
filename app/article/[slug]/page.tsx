import { supabase } from '@/lib/supabase'
import Header from '@/components/Header'
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

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { slug } = await params
  const [article, sections] = await Promise.all([
    getArticle(slug),
    getSections()
  ])

  if (!article) {
    notFound()
  }

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
      
      <main className="container mx-auto px-4 py-8">
        <article className="max-w-4xl mx-auto">
          {/* Article Header */}
          <header className="mb-8">
            <div className="mb-4">
              <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                {article.section_slug.toUpperCase()}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              {article.title}
            </h1>
            
            <div className="flex items-center text-gray-600 text-sm mb-4">
              <span>By {article.source_name}</span>
              <span className="mx-2">•</span>
              <span>{formatDate(article.created_at)}</span>
            </div>
            
            {article.summary && (
              <p className="text-xl text-gray-700 leading-relaxed">
                {article.summary}
              </p>
            )}
          </header>

          {/* Article Content */}
          {article.scraped_content && (
            <div className="prose prose-lg max-w-none">
              <div 
                className="text-gray-800 leading-relaxed"
                dangerouslySetInnerHTML={{ 
                  __html: article.scraped_content.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>')
                }}
              />
            </div>
          )}

          {/* Article Footer */}
          <footer className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  Originally published by {article.source_name}
                </p>
                <a 
                  href={article.source_url}
                  target="_blank"
                  rel="noopener nofollow ugc"
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View original article →
                </a>
              </div>
              
              {article.tags && article.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {article.tags.map((tag: string) => (
                    <span 
                      key={tag}
                      className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </footer>
        </article>
      </main>
    </div>
  )
}

export const revalidate = 60
