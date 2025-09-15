import Link from 'next/link'

interface TagChipProps {
  tag: string
  className?: string
}

export default function TagChip({ tag, className = '' }: TagChipProps) {
  return (
    <Link 
      href={`/tag/${tag}`}
      className={`tag-chip ${className}`}
    >
      #{tag}
    </Link>
  )
}
