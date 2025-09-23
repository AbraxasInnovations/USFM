'use client'

import { useEffect, useRef } from 'react'

declare global {
  interface Window {
    adsbygoogle: any[]
  }
}

interface AdSenseProps {
  adClient: string
  adSlot: string
  adFormat?: string
  fullWidthResponsive?: boolean
  style?: React.CSSProperties
}

export default function AdSense({ 
  adClient, 
  adSlot, 
  adFormat = 'auto',
  fullWidthResponsive = true,
  style = { display: 'block' }
}: AdSenseProps) {
  const adRef = useRef<HTMLDivElement>(null)
  const adInitialized = useRef(false)

  useEffect(() => {
    try {
      if (typeof window !== 'undefined' && window.adsbygoogle && adRef.current && !adInitialized.current) {
        // Check if this specific ad element already has ads
        const adElement = adRef.current.querySelector('.adsbygoogle')
        if (adElement && !adElement.hasAttribute('data-adsbygoogle-status')) {
          // Ensure the ad element has proper dimensions
          const rect = adElement.getBoundingClientRect()
          if (rect.width > 0) {
            (window.adsbygoogle = window.adsbygoogle || []).push({})
            adInitialized.current = true
          } else {
            // If no width, wait a bit and try again
            setTimeout(() => {
              const retryRect = adElement.getBoundingClientRect()
              if (retryRect.width > 0 && !adInitialized.current) {
                (window.adsbygoogle = window.adsbygoogle || []).push({})
                adInitialized.current = true
              }
            }, 100)
          }
        }
      }
    } catch (error) {
      console.error('AdSense error:', error)
    }
  }, [])

  return (
    <div ref={adRef} style={{ width: '100%', minWidth: '300px' }}>
      <ins
        className="adsbygoogle"
        style={{
          ...style,
          width: '100%',
          minWidth: '300px',
          display: 'block'
        }}
        data-ad-client={adClient}
        data-ad-slot={adSlot}
        data-ad-format={adFormat}
        data-full-width-responsive={fullWidthResponsive.toString()}
      />
    </div>
  )
}
