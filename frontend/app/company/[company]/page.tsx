import Header from '../../components/Header'

export default function CompanyPage({ params }: { params: { company: string } }) {
  return (
    <main>
      <Header />
      <h2 className="text-2xl font-semibold">Company: {params.company}</h2>
      <p className="text-gray-300 mt-4">Placeholder for company intelligence page.</p>
    </main>
  )
}
