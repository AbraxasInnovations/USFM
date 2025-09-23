import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    // Get all published posts
    const { data: allPosts, error: postsError } = await supabase
      .from('posts')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })

    if (postsError) {
      console.error('Error fetching posts:', postsError)
      return NextResponse.json({ error: 'Failed to fetch posts' }, { status: 500 })
    }

    // Get sections
    const { data: sections, error: sectionsError } = await supabase
      .from('sections')
      .select('*')
      .order('name')

    if (sectionsError) {
      console.error('Error fetching sections:', sectionsError)
      return NextResponse.json({ error: 'Failed to fetch sections' }, { status: 500 })
    }

    // Smart content management logic
    const sectionThresholds = {
      'ma': 3,
      'lbo': 3,
      'reg': 3,
      'cap': 5,
      'rumor': 2,
      'all': 30
    }

    const fallbackRetentionDays = 7
    const cutoffTime = new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    const fallbackCutoff = new Date(Date.now() - fallbackRetentionDays * 24 * 60 * 60 * 1000) // 7 days ago
    
    // Debug logging (can be removed in production)
    // console.log('Smart Content API Debug:')
    // console.log('Cutoff time (2h ago):', cutoffTime.toISOString())
    // console.log('Fallback cutoff (7d ago):', fallbackCutoff.toISOString())

    // Group posts by section
    const postsBySection: { [key: string]: any[] } = {}
    for (const post of allPosts || []) {
      const section = post.section_slug || 'cap'
      if (!postsBySection[section]) {
        postsBySection[section] = []
      }
      postsBySection[section].push(post)
    }

    // Apply smart content management to each section
    const smartContent: { [key: string]: any[] } = {}
    
    for (const section of sections || []) {
      const sectionSlug = section.slug
      const threshold = sectionThresholds[sectionSlug as keyof typeof sectionThresholds] || 3
      const newPosts = postsBySection[sectionSlug] || []
      
      // Filter for recent posts (last 2 hours)
      const recentPosts = newPosts.filter(post => 
        new Date(post.created_at) > cutoffTime
      )
      
      if (recentPosts.length >= threshold) {
        // Use recent posts if we have enough
        smartContent[sectionSlug] = recentPosts.slice(0, threshold)
      } else {
        // Need fallback posts
        const needed = threshold - recentPosts.length
        
        // Debug logging for REG section (can be removed in production)
        // if (sectionSlug === 'reg') {
        //   console.log(`REG section: ${recentPosts.length} recent, need ${needed} fallback`)
        //   console.log(`REG total posts: ${newPosts.length}`)
        // }
        
        // Get fallback posts (older than 2 hours, newer than 7 days)
        const fallbackPosts = newPosts.filter(post => {
          const postDate = new Date(post.created_at)
          const isInRange = postDate <= cutoffTime && postDate >= fallbackCutoff
          
          // Debug logging for REG section (can be removed in production)
          // if (sectionSlug === 'reg' && post.scraped_content) {
          //   console.log(`REG scraped post: ${post.title}`)
          //   console.log(`  Post date: ${postDate.toISOString()}`)
          //   console.log(`  Cutoff: ${cutoffTime.toISOString()}`)
          //   console.log(`  Fallback cutoff: ${fallbackCutoff.toISOString()}`)
          //   console.log(`  Is in range: ${isInRange}`)
          // }
          
          return isInRange
        })
        
        // Debug logging for REG section (can be removed in production)
        // if (sectionSlug === 'reg') {
        //   console.log(`REG fallback posts after filter: ${fallbackPosts.length}`)
        //   const scrapedFallback = fallbackPosts.filter(p => p.scraped_content)
        //   console.log(`REG scraped fallback posts: ${scrapedFallback.length}`)
        // }
        
        // Sort fallback posts: scraped content first, then by created_at desc
        fallbackPosts.sort((a, b) => {
          // Prioritize scraped content
          if (a.scraped_content && !b.scraped_content) return -1
          if (!a.scraped_content && b.scraped_content) return 1
          
          // If both are scraped or both are not scraped, sort by date
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        })
        
        // Debug logging for REG section (can be removed in production)
        // if (sectionSlug === 'reg') {
        //   console.log(`REG after sorting: ${fallbackPosts.length} fallback posts`)
        //   const scrapedAfterSort = fallbackPosts.filter(p => p.scraped_content)
        //   console.log(`REG scraped after sort: ${scrapedAfterSort.length}`)
        //   if (scrapedAfterSort.length > 0) {
        //     console.log(`REG scraped post position: ${fallbackPosts.findIndex(p => p.scraped_content)}`)
        //   }
        // }
        
        // Combine recent and fallback posts
        const combinedPosts = [...recentPosts, ...fallbackPosts.slice(0, needed)]
        smartContent[sectionSlug] = combinedPosts.slice(0, threshold)
        
        // Debug logging for REG section (can be removed in production)
        // if (sectionSlug === 'reg') {
        //   console.log(`REG final result: ${smartContent[sectionSlug].length} posts`)
        //   const finalScraped = smartContent[sectionSlug].filter(p => p.scraped_content)
        //   console.log(`REG final scraped: ${finalScraped.length}`)
        // }
      }
    }

    // Handle homepage content
    const allRecentPosts = allPosts?.filter(post => 
      new Date(post.created_at) > cutoffTime
    ) || []
    
    if (allRecentPosts.length >= 30) {
      smartContent['homepage'] = allRecentPosts.slice(0, 30)
    } else {
      const needed = 30 - allRecentPosts.length
      const fallbackPosts = allPosts?.filter(post => {
        const postDate = new Date(post.created_at)
        return postDate <= cutoffTime && postDate >= fallbackCutoff
      }) || []
      
      // Sort fallback posts: scraped content first, then by created_at desc
      fallbackPosts.sort((a, b) => {
        // Prioritize scraped content
        if (a.scraped_content && !b.scraped_content) return -1
        if (!a.scraped_content && b.scraped_content) return 1
        
        // If both are scraped or both are not scraped, sort by date
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      })
      
      smartContent['homepage'] = [...allRecentPosts, ...fallbackPosts.slice(0, needed)].slice(0, 30)
    }

    return NextResponse.json({
      smartContent,
      stats: {
        totalPosts: allPosts?.length || 0,
        recentPosts: allRecentPosts.length,
        sections: Object.keys(smartContent).length
      },
      debug: {
        cutoffTime: cutoffTime.toISOString(),
        fallbackCutoff: fallbackCutoff.toISOString(),
        regPosts: postsBySection['reg']?.length || 0,
        regScraped: postsBySection['reg']?.filter(p => p.scraped_content).length || 0,
        regRecent: smartContent['reg']?.filter(p => new Date(p.created_at) > cutoffTime).length || 0,
        regFallback: smartContent['reg']?.filter(p => {
          const postDate = new Date(p.created_at)
          return postDate <= cutoffTime && postDate >= fallbackCutoff
        }).length || 0,
        regScrapedInResponse: smartContent['reg']?.filter(p => p.scraped_content).length || 0
      }
    })

  } catch (error) {
    console.error('Error in smart content API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}