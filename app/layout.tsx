import type { Metadata } from 'next'
import { Oswald } from 'next/font/google'
import './globals.css'

const oswald = Oswald({
  weight: '500',
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'US Finance Moves',
  description: 'US Finance Deal Feed - M&A, LBO, take-privates, antitrust, major financings',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Google AdSense */}
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
          crossOrigin="anonymous"
        ></script>
      </head>
      <body className={oswald.className}>
        {children}
        <footer style={{
          backgroundColor: '#f8f9fa',
          color: '#333',
          padding: '64px 32px 32px',
          marginTop: '64px',
          width: '100%',
          borderTop: '1px solid #e5e7eb'
        }}>
          <div style={{maxWidth: '1400px', margin: '0 auto'}}>
            <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '48px', marginBottom: '48px'}}>
              {/* Company Info */}
              <div>
                <div style={{marginBottom: '32px'}}>
                  <span style={{fontSize: '4.125rem', fontWeight: '700', color: '#6b7280', display: 'inline', lineHeight: '1', marginRight: '0.5rem', letterSpacing: 'normal'}}>
                    US
                  </span>
                  <span style={{fontSize: '4.125rem', fontWeight: '700', color: '#6b7280', display: 'inline', lineHeight: '1', marginRight: '0.5rem', letterSpacing: 'normal'}}>
                    Finance
                  </span>
                  <span style={{fontSize: '4.125rem', fontWeight: '700', color: '#374151', display: 'inline', lineHeight: '1', letterSpacing: 'normal'}}>
                    Moves
                  </span>
                </div>
                <p style={{fontSize: '15px', color: '#6b7280', lineHeight: '1.7', marginBottom: '24px'}}>
                  Your comprehensive source for US financial deal news, including M&A, LBO, regulatory actions, and capital market developments.
                </p>
                <div style={{fontSize: '13px', color: '#9ca3af'}}>
                  © 2025 US Finance Moves. All rights reserved.
                </div>
              </div>

              {/* Quick Links */}
              <div>
                <h4 style={{fontSize: '18px', fontWeight: '600', marginBottom: '24px', color: '#1f2937'}}>
                  Sections
                </h4>
                <ul style={{listStyle: 'none', padding: 0, margin: 0}}>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/section/ma" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Mergers & Acquisitions
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/section/lbo" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      LBO & Private Equity
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/section/reg" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Regulatory
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/section/cap" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Capital Markets
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/section/rumor" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      DeFi/Crypto
                    </a>
                  </li>
                </ul>
              </div>

              {/* Resources */}
              <div>
                <h4 style={{fontSize: '18px', fontWeight: '600', marginBottom: '24px', color: '#1f2937'}}>
                  Resources
                </h4>
                <ul style={{listStyle: 'none', padding: 0, margin: 0}}>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/search" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Search
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="/archive" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Archive
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="https://www.sec.gov/edgar" target="_blank" rel="noopener nofollow" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      SEC EDGAR
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="https://www.ftc.gov/news-events" target="_blank" rel="noopener nofollow" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      FTC News
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="https://www.justice.gov/atr" target="_blank" rel="noopener nofollow" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      DOJ Antitrust
                    </a>
                  </li>
                  <li style={{marginBottom: '12px'}}>
                    <a href="https://twitter.com/usfinancemoves" target="_blank" rel="noopener nofollow" style={{fontSize: '15px', color: '#6b7280', textDecoration: 'none', transition: 'color 0.2s'}}>
                      Twitter
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            {/* Bottom Bar */}
            <div style={{borderTop: '1px solid #e5e7eb', paddingTop: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '24px'}}>
              <div style={{fontSize: '13px', color: '#9ca3af'}}>
                Data sourced from SEC EDGAR, government agencies, and financial news providers.
              </div>
              <div style={{fontSize: '13px', color: '#9ca3af'}}>
                Last updated: {new Date().toLocaleDateString()}
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
