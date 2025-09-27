import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'
import { revalidatePath } from 'next/cache'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(request: NextRequest) {
  try {
    // Basic authentication check (you can enhance this later)
    const authHeader = request.headers.get('authorization')
    const expectedAuth = process.env.ADMIN_PASSWORD
    
    if (!expectedAuth) {
      return NextResponse.json({ error: 'Admin authentication not configured' }, { status: 500 })
    }

    // For now, we'll skip auth in development, but you should add proper auth
    // if (authHeader !== `Bearer ${expectedAuth}`) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // }

    const formData = await request.formData()
    
    // Extract form data
    const author = formData.get('author') as string
    const headline = formData.get('headline') as string
    const content = formData.get('content') as string
    const summary = formData.get('summary') as string
    const tags = formData.get('tags') as string
    const publishDate = formData.get('publishDate') as string
    const articleSlug = formData.get('articleSlug') as string
    const imageFile = formData.get('image') as File | null

    // Validate required fields
    if (!author || !headline || !content) {
      return NextResponse.json({ error: 'Author, headline, and content are required' }, { status: 400 })
    }

    let imageUrl = null

    // Handle image upload if provided
    if (imageFile && imageFile.size > 0) {
      try {
        // Create custom images directory if it doesn't exist
        const customImagesDir = join(process.cwd(), 'public', 'images', 'custom')
        await mkdir(customImagesDir, { recursive: true })

        // Generate unique filename
        const timestamp = Date.now()
        const fileExtension = imageFile.name.split('.').pop() || 'jpg'
        const fileName = `custom-${timestamp}.${fileExtension}`
        const filePath = join(customImagesDir, fileName)

        // Convert file to buffer and save
        const bytes = await imageFile.arrayBuffer()
        const buffer = Buffer.from(bytes)
        await writeFile(filePath, buffer)

        // Set the image URL
        imageUrl = `/images/custom/${fileName}`
      } catch (imageError) {
        console.error('Error saving image:', imageError)
        return NextResponse.json({ error: 'Failed to save image' }, { status: 500 })
      }
    }

    // Process tags
    const tagArray = tags ? tags.split(',').map(tag => tag.trim()).filter(tag => tag) : []

    // Generate content hash for deduplication
    const contentHash = Buffer.from(`${headline}-${content}`).toString('base64')

    // Prepare post data
    const postData = {
      title: headline,
      summary: summary || content.substring(0, 200) + '...',
      excerpt: summary || content.substring(0, 200) + '...',
      source_name: author,
      source_url: '', // Custom articles don't have external sources
      section_slug: 'written', // Custom articles go to 'written' section
      tags: tagArray,
      status: 'published',
      origin_type: 'CUSTOM',
      image_url: imageUrl,
      scraped_content: content,
      article_slug: articleSlug,
      created_at: publishDate ? new Date(publishDate).toISOString() : new Date().toISOString(),
      content_hash: contentHash
    }

    // Insert into database
    const { data, error } = await supabase
      .from('posts')
      .insert([postData])
      .select()
      .single()

    if (error) {
      console.error('Database error:', error)
      return NextResponse.json({ error: 'Failed to save article to database' }, { status: 500 })
    }

    // Revalidate the homepage and written articles section
    try {
      revalidatePath('/')
      revalidatePath('/section/written')
    } catch (revalidateError) {
      console.error('Revalidation error:', revalidateError)
      // Don't fail the request if revalidation fails
    }

    return NextResponse.json({
      success: true,
      articleId: data.id,
      articleSlug: articleSlug,
      message: 'Article uploaded successfully'
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
