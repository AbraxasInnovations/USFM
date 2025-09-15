import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { paths, secret } = body

    // Verify the secret
    if (secret !== process.env.REVALIDATE_SECRET) {
      return NextResponse.json(
        { error: 'Invalid secret' },
        { status: 401 }
      )
    }

    // Validate paths
    if (!paths || !Array.isArray(paths)) {
      return NextResponse.json(
        { error: 'Invalid paths' },
        { status: 400 }
      )
    }

    // Revalidate each path
    const revalidatedPaths = []
    for (const path of paths) {
      try {
        revalidatePath(path)
        revalidatedPaths.push(path)
      } catch (error) {
        console.error(`Error revalidating path ${path}:`, error)
      }
    }

    return NextResponse.json({
      revalidated: true,
      paths: revalidatedPaths,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Revalidation error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
