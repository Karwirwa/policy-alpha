import type { Sector } from '../../lib/api/kenya'

type SectorSummaryProps = {
  sectors: Sector[]
  selectedSector: string
  onSelect: (sector: string) => void
}

export default function SectorSummary({
  sectors,
  selectedSector,
  onSelect,
}: SectorSummaryProps) {
  return (
    <section aria-label="Opportunities by sector">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Sector overview</h2>
        <span className="text-xs text-gray-500">Select a sector to filter</span>
      </div>
      <div className="-mx-1 flex gap-3 overflow-x-auto px-1 pb-3">
        <button
          type="button"
          onClick={() => onSelect('')}
          aria-pressed={!selectedSector}
          className={`min-w-32 rounded-xl border p-4 text-left transition ${
            !selectedSector
              ? 'border-indigo-400/50 bg-indigo-500/10'
              : 'border-white/10 bg-white/[0.03] hover:border-white/20'
          }`}
        >
          <span className="block text-sm font-semibold text-white">All sectors</span>
          <span className="mt-2 block text-xs text-gray-400">View every tender</span>
        </button>
        {sectors.map((sector) => {
          const selected = selectedSector === sector.name
          return (
            <button
              key={sector.name}
              type="button"
              onClick={() => onSelect(selected ? '' : sector.name)}
              aria-pressed={selected}
              className={`min-w-36 rounded-xl border p-4 text-left transition ${
                selected
                  ? 'border-indigo-400/50 bg-indigo-500/10'
                  : 'border-white/10 bg-white/[0.03] hover:border-white/20'
              }`}
            >
              <span className="block text-sm font-semibold capitalize text-white">
                {sector.name}
              </span>
              <span className="mt-1 block text-xs text-gray-400">
                {sector.count} {sector.count === 1 ? 'tender' : 'tenders'}
              </span>
              <span className="mt-3 block text-sm font-medium text-indigo-200">
                Avg. {Math.round(sector.avg_score)}
              </span>
            </button>
          )
        })}
      </div>
    </section>
  )
}
