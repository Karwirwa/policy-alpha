import Header from '../../components/Header'
import dynamic from 'next/dynamic'

const CrawlerDashboard = dynamic(() => import('../../components/CrawlerDashboard'), { ssr: false })

export default function PipelinePage() {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Pipeline & Crawler Monitor</h2>
      <CrawlerDashboard />
    </main>
  )
}
