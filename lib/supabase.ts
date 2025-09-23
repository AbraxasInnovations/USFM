import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for our database
export interface Post {
  id: string
  created_at: string
  updated_at: string
  title: string
  summary: string | null
  excerpt: string | null
  source_name: string
  source_url: string
  section_slug: string
  tags: string[]
  content_hash: string
  status: 'published' | 'hidden'
  origin_type: 'SEC' | 'USGOV' | 'PRESS' | 'MEDIA' | 'RUMOR' | 'SCRAPED' | 'CRYPTO'
  image_url: string | null
  scraped_content: string | null
  article_slug: string | null
}

export interface Section {
  slug: string
  name: string
  created_at: string
}
