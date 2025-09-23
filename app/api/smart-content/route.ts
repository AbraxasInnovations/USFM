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
      'cap': 3,
      'rumor': 3,
      'all': 20
    }

    const fallbackRetentionDays = 14
    const cutoffTime = new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    const fallbackCutoff = new Date(Date.now() - fallbackRetentionDays * 24 * 60 * 60 * 1000) // 14 days ago
    
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
      
      // Sort all posts by priority: scraped content first, then by created_at desc
      const sortedPosts = [...newPosts].sort((a, b) => {
        // Prioritize scraped content
        if (a.scraped_content && !b.scraped_content) return -1
        if (!a.scraped_content && b.scraped_content) return 1
        
        // If both are scraped or both are not scraped, sort by date
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      })
      
      // Filter for recent posts (last 2 hours) from sorted list
      const recentPosts = sortedPosts.filter(post => 
        new Date(post.created_at) > cutoffTime
      )
      
      if (recentPosts.length >= threshold) {
        // Use recent posts if we have enough
        smartContent[sectionSlug] = recentPosts.slice(0, threshold)
        console.log(`✅ Section ${sectionSlug}: Using ${recentPosts.length} recent posts`)
      } else {
        // Not enough recent posts - use the best available posts to fill to threshold
        const needed = threshold
        const availablePosts = sortedPosts.slice(0, needed)
        
        // Always ensure we have exactly the threshold number of posts
        if (availablePosts.length >= needed) {
          smartContent[sectionSlug] = availablePosts
        } else {
          // If we don't have enough posts in this section, use what we have
          smartContent[sectionSlug] = availablePosts
        }
        
        console.log(`📋 Section ${sectionSlug}: Using ${smartContent[sectionSlug].length}/${threshold} posts (${recentPosts.length} recent)`)
      }
    }

    // Final safety net: if any section is still empty, try to populate with related content
    for (const section of sections || []) {
      const sectionSlug = section.slug
      const threshold = sectionThresholds[sectionSlug as keyof typeof sectionThresholds] || 3
      
      if (!smartContent[sectionSlug] || smartContent[sectionSlug].length < threshold) {
        const currentCount = smartContent[sectionSlug]?.length || 0
        const needed = threshold - currentCount
        console.log(`🚨 Section ${sectionSlug}: Only ${currentCount}/${threshold} posts, need ${needed} more`)
        
        // Try to find related content from other sections
        let emergencyPosts: any[] = []
        
        // For LBO/PE, try M&A content
        if (sectionSlug === 'lbo') {
          emergencyPosts = (smartContent['ma'] || []).filter(post => 
            post.title.toLowerCase().includes('private') || 
            post.title.toLowerCase().includes('equity') ||
            post.title.toLowerCase().includes('buyout')
          )
        }
        
        // For regulatory, try M&A content with regulatory keywords
        if (sectionSlug === 'reg') {
          emergencyPosts = (smartContent['ma'] || []).filter(post => 
            post.title.toLowerCase().includes('approval') || 
            post.title.toLowerCase().includes('regulatory') ||
            post.title.toLowerCase().includes('antitrust')
          )
        }
        
        // For crypto/rumors, try any content with crypto keywords
        if (sectionSlug === 'rumor') {
          emergencyPosts = Object.values(smartContent).flat().filter(post => 
            post && (
              post.title.toLowerCase().includes('crypto') ||
              post.title.toLowerCase().includes('bitcoin') ||
              post.title.toLowerCase().includes('blockchain') ||
              post.title.toLowerCase().includes('altcoin') ||
              post.tags?.some(tag => ['crypto', 'bitcoin', 'blockchain', 'altcoin'].includes(tag.toLowerCase()))
            )
          )
        }
        
        // If still no emergency posts, use any recent content from other sections
        if (emergencyPosts.length === 0) {
          const allOtherPosts = Object.values(smartContent).flat().filter(post => post)
          emergencyPosts = allOtherPosts
        }
        
        // Add emergency posts to existing content
        const existingPosts = smartContent[sectionSlug] || []
        const additionalPosts = emergencyPosts.slice(0, needed)
        smartContent[sectionSlug] = [...existingPosts, ...additionalPosts].slice(0, threshold)
        console.log(`🚨 Emergency fallback for ${sectionSlug}: Added ${additionalPosts.length} posts, total: ${smartContent[sectionSlug].length}`)
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