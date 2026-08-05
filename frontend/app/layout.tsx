import './globals.css'
import React from 'react'

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
            {children}
          </div>
        </div>
      </body>
    </html>
  )
}
