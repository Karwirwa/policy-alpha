import { fetcher } from '../../lib/fetcher'
import Header from '../../components/Header'

export default async function Dashboard() {
  let topOpportunities = []
  let latestEvidence = []
  try {
    topOpportunities = await fetcher('/api/v1/opportunity/top')
    latestEvidence = await fetcher('/api/v1/evidence/latest')
  } catch (e) {
    // fail silently for now
  }

  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-glass p-4">
          <h4 className="font-medium mb-2">Top Opportunities</h4>
          <ul className="text-sm text-gray-200">
            {topOpportunities.length === 0 ? <li>No data</li> : topOpportunities.map((t: any) => (
              <li key={t.company_id} className="py-2 border-b border-gray-700">{t.company_name} — {t.score}</li>
            ))}
          </ul>
        </div>

        <div className="card-glass p-4 lg:col-span-2">
          <h4 className="font-medium mb-2">Latest Evidence</h4>
          <ul className="text-sm text-gray-200">
            {latestEvidence.length === 0 ? <li>No evidence</li> : latestEvidence.map((e: any) => (
              <li key={e.id} className="py-2 border-b border-gray-700">{e.title} — {e.source_reference}</li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  )
}
