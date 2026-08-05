import './globals.css'
import React from 'react'
import Providers from '../components/Providers'

export const metadata = {
  title: 'Policy Alpha',
  description: 'Government Opportunity Intelligence Platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <div className="min-h-screen">
          <div className="max-w-[1400px] mx-auto px-6 py-6">
            {/* Providers is a client component that wraps React Query and other client-only providers */}
            <Providers>{children}</Providers>
          </div>
        </div>
      </body>
    </html>
  )
}
