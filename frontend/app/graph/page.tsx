import Header from '../../components/Header'
import dynamic from 'next/dynamic'

const RelationshipGraph = dynamic(() => import('../../components/RelationshipGraph'), { ssr: false })

export default function GraphPage() {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Knowledge Graph</h2>
      <RelationshipGraph />
    </main>
  )
}
