import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function GET(request: NextRequest) {
  try {
    // Fetch all custom articles, ordered by creation date (newest first)
    const { data: articles, error } = await supabase
      .from('posts')
      .select('*')
      .eq('origin_type', 'CUSTOM')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching articles:', error)
      return NextResponse.json({ error: 'Failed to fetch articles' }, { status: 500 })
    }

    return NextResponse.json({ articles })

  } catch (error) {
    console.error('Error in articles API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
