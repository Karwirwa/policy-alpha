import Header from '../../../components/Header'
import dynamic from 'next/dynamic'

const CountryDashboard = dynamic(() => import('../../../components/CountryDashboard'), { ssr: false })

export default function CountryPage({ params }: { params: { country: string } }) {
  const country = params.country
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold mb-4">Country: {country}</h2>
      <CountryDashboard country={country} />
    </main>
  )
}
