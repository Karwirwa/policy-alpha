import Header from '../../components/Header'
import dynamic from 'next/dynamic'

const DashboardMain = dynamic(() => import('../../components/DashboardMain'), { ssr: false })

export default function Dashboard() {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>
      <DashboardMain />
    </main>
  )
}
