import { MetadataRoute } from 'next'
import { supabase } from '@/lib/supabase'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Get all published articles
  const { data: posts } = await supabase
    .from('posts')
    .select('article_slug, updated_at, created_at')
    .eq('status', 'published')
    .order('created_at', { ascending: false })

  // Get all sections
  const { data: sections } = await supabase
    .from('sections')
    .select('slug')
    .order('created_at')

  const baseUrl = 'https://www.usfinancemoves.com'

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 1,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
  ]

  // Section pages
  const sectionPages: MetadataRoute.Sitemap = sections?.map((section) => ({
    url: `${baseUrl}/section/${section.slug}`,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 0.9,
  })) || []

  // Article pages
  const articlePages: MetadataRoute.Sitemap = posts?.map((post) => ({
    url: `${baseUrl}/article/${post.article_slug}`,
    lastModified: new Date(post.updated_at || post.created_at),
    changeFrequency: 'weekly',
    priority: 0.7,
  })) || []

  return [...staticPages, ...sectionPages, ...articlePages]
}
