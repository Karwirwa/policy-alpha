import Header from '../../components/Header'
import dynamic from 'next/dynamic'

const EvidenceExplorer = dynamic(() => import('../../components/EvidenceExplorer'), { ssr: false })

export default function EvidencePage() {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Evidence Explorer</h2>
      <EvidenceExplorer />
    </main>
  )
}
