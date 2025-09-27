import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function DELETE(request: NextRequest) {
  try {
    // Create Supabase client inside the function to avoid build-time issues
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    )
    const { articleId } = await request.json()

    if (!articleId) {
      return NextResponse.json({ error: 'Article ID is required' }, { status: 400 })
    }

    // First, get the article to check if it's a custom article and get image info
    const { data: article, error: fetchError } = await supabase
      .from('posts')
      .select('*')
      .eq('id', articleId)
      .eq('origin_type', 'CUSTOM')
      .single()

    if (fetchError || !article) {
      return NextResponse.json({ error: 'Article not found or not a custom article' }, { status: 404 })
    }

    // Delete the article from the database
    const { error: deleteError } = await supabase
      .from('posts')
      .delete()
      .eq('id', articleId)

    if (deleteError) {
      console.error('Error deleting article:', deleteError)
      return NextResponse.json({ error: 'Failed to delete article' }, { status: 500 })
    }

    // If the article had an image, delete it from storage
    if (article.image_url && article.image_url.includes('/images/custom/')) {
      const imagePath = article.image_url.split('/images/custom/')[1]
      const { error: imageDeleteError } = await supabase.storage
        .from('images')
        .remove([`custom/${imagePath}`])

      if (imageDeleteError) {
        console.error('Error deleting image:', imageDeleteError)
        // Don't fail the request if image deletion fails
      }
    }

    return NextResponse.json({ success: true, message: 'Article deleted successfully' })

  } catch (error) {
    console.error('Error in delete API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
