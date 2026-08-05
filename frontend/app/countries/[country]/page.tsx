import Header from '../../components/Header'

export default function CountryPage({ params }: { params: { country: string } }) {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold">Country: {params.country}</h2>
      <p className="text-gray-300 mt-4">Placeholder for country intelligence page.</p>
    </main>
  )
}
