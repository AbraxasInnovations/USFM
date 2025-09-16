'use client'

import Link from 'next/link'
import { Section } from '@/lib/supabase'
import { useState, useEffect } from 'react'

interface HeaderProps {
  sections: Section[]
}

export default function Header({ sections }: HeaderProps) {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      setIsScrolled(scrollTop > 100)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <>
      {/* Initial compact section */}
      <section className={`hero-section ${isScrolled ? 'scrolled' : ''}`}>
        <div className="hero-content">
          <div className="hero-header">
            <Link href="/" className="hero-logo">
              <span className="logo-main">US</span>
              <span className="logo-financial">Financial</span>
              <span className="logo-moves">Moves</span>
            </Link>
            <p className="hero-tagline">The only free news source for serious moves across finance</p>
          </div>
          <nav className="hero-nav">
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
      </section>

      {/* Sticky compact header */}
      <header className={`sticky-header ${isScrolled ? 'visible' : ''}`}>
        <div className="container">
          <Link href="/" className="compact-logo">
            <span className="logo-main">US</span>
            <span className="logo-financial">Financial</span>
            <span className="logo-moves">Moves</span>
          </Link>
          <nav className="compact-nav">
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
    </>
  )
}
