import { useState } from 'react'

interface PostImageProps {
  imageUrl: string | null
  title: string
  sectionSlug: string
  className?: string
}

export default function PostImage({ imageUrl, title, sectionSlug, className = '' }: PostImageProps) {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  // Fallback emojis based on section
  const getFallbackEmoji = (section: string) => {
    switch (section) {
      case 'ma': return '🤝'
      case 'lbo': return '💰'
      case 'reg': return '⚖️'
      case 'cap': return '📈'
      case 'rumor': return '👀'
      default: return '📊'
    }
  }

  // If no image URL or image failed to load, show fallback
  if (!imageUrl || imageError) {
    return (
      <div className={`placeholder-image ${className}`}>
        {getFallbackEmoji(sectionSlug)}
      </div>
    )
  }

  return (
    <div className={`post-image-container ${className}`}>
      {imageLoading && (
        <div className="image-loading">
          {getFallbackEmoji(sectionSlug)}
        </div>
      )}
      <img
        src={imageUrl}
        alt={title}
        className={`post-image ${imageLoading ? 'loading' : 'loaded'}`}
        onLoad={() => setImageLoading(false)}
        onError={() => {
          setImageError(true)
          setImageLoading(false)
        }}
        loading="lazy"
      />
    </div>
  )
}
