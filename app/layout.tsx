import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BuckBounty - AI Personal Finance',
  description: 'Your AI-powered personal finance assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
