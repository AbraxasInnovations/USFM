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
      </body>
    </html>
  )
}
