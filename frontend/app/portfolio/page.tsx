import Header from '../../components/Header'
import dynamic from 'next/dynamic'

const PortfolioPanel = dynamic(() => import('../../components/PortfolioPanel'), { ssr: false })

export default function PortfolioPage() {
  // NOTE: defaultUuid should be replaced with user's portfolio selection
  const defaultUuid = 'default'
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Portfolio</h2>
      <PortfolioPanel portfolioUuid={defaultUuid} />
    </main>
  )
}
