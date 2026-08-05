import Link from 'next/link'

export default async function Home() {
  return (
    <main>
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-semibold">Policy Alpha</h1>
          <p className="text-muted mt-2 text-gray-300">Government Opportunity Intelligence Platform</p>
        </div>
        <div>
          <Link href="/dashboard" className="px-4 py-2 bg-indigo-600 rounded-md shadow hover:bg-indigo-500">Open Dashboard</Link>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-glass p-6 rounded-lg">
          <h3 className="text-xl font-medium">Supported Countries</h3>
          <ul className="mt-4 space-y-2 text-gray-200">
            <li>🇰🇪 Kenya</li>
            <li>🇺🇸 United States</li>
            <li>🇬🇧 United Kingdom</li>
            <li>🇨🇦 Canada</li>
          </ul>
        </div>

        <div className="card-glass p-6 rounded-lg">
          <h3 className="text-xl font-medium">Platform Summary</h3>
          <p className="mt-3 text-gray-300">Live data powered by government evidence. Dashboard shows top opportunities, latest evidence, and crawler/pipeline status.</p>
          <div className="mt-4 space-y-2 text-sm text-gray-200">
            <div>Companies: —</div>
            <div>Projects: —</div>
            <div>Evidence: —</div>
            <div>Opportunity Scores: —</div>
          </div>
        </div>

        <div className="card-glass p-6 rounded-lg">
          <h3 className="text-xl font-medium">Get Started</h3>
          <p className="mt-3 text-gray-300">Open the intelligence dashboard to explore companies, evidence, and opportunities.</p>
          <div className="mt-4">
            <Link href="/dashboard" className="px-4 py-2 bg-indigo-600 rounded-md shadow hover:bg-indigo-500">Open Dashboard</Link>
          </div>
        </div>
      </section>

      <footer className="mt-12 text-sm text-gray-500">© Policy Alpha</footer>
    </main>
  )
}
