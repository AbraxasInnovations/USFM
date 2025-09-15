import Link from 'next/link'
import { Section } from '@/lib/supabase'

interface HeaderProps {
  sections: Section[]
}

export default function Header({ sections }: HeaderProps) {
  return (
    <header className="header">
      <div className="container">
        <Link href="/" className="logo">
          US Financial Moves
        </Link>
        <nav className="nav">
          <ul>
            {sections.map((section) => (
              <li key={section.slug}>
                <Link href={section.slug === 'all' ? '/' : `/section/${section.slug}`}>
                  {section.name}
                </Link>
              </li>
            ))}
            <li>
              <Link href="/search">Search</Link>
            </li>
            <li>
              <Link href="/archive">Archive</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  )
}
