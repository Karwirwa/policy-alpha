'use client'
import Link from 'next/link'

export default function Header() {
  return (
    <header className="flex items-center justify-between mb-6">
      <div className="flex items-center space-x-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold">PA</div>
        <div>
          <Link href="/" className="text-lg font-semibold">Policy Alpha</Link>
          <div className="text-sm text-gray-400">Government Opportunity Intelligence</div>
        </div>
      </div>

      <nav className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <Link href="/dashboard" className="text-sm text-gray-200 hover:underline">Dashboard</Link>
        <Link href="/kenya" className="text-sm text-gray-200 hover:underline">Kenya</Link>
        <Link href="/graph" className="text-sm text-gray-200 hover:underline">Graph</Link>
        <Link href="/portfolio" className="text-sm text-gray-200 hover:underline">Portfolio</Link>
      </nav>
    </header>
  )
}
