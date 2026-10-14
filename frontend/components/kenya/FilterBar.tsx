import type { Ministry, Sector } from '../../lib/api/kenya'

export type OpportunityFilters = {
  selectedSector: string
  selectedMinistry: string
  minScore: number
  search: string
  includeIllustrative: boolean
}

type FilterBarProps = {
  sectors: Sector[]
  ministries: Ministry[]
  selectedSector: string
  selectedMinistry: string
  minScore: number
  search: string
  includeIllustrative: boolean
  onFilterChange: (filters: Partial<OpportunityFilters>) => void
}

const controlClass =
  'min-h-11 w-full rounded-lg border border-white/10 bg-[#111821] px-3 text-sm text-gray-100 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20'

export default function FilterBar({
  sectors,
  ministries,
  selectedSector,
  selectedMinistry,
  minScore,
  search,
  includeIllustrative,
  onFilterChange,
}: FilterBarProps) {
  return (
    <section
      aria-label="Filter opportunities"
      className="grid grid-cols-1 gap-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4 sm:grid-cols-2 xl:grid-cols-5"
    >
      <label className="text-xs font-medium text-gray-400">
        Sector
        <select
          className={`${controlClass} mt-1.5`}
          value={selectedSector}
          onChange={(event) =>
            onFilterChange({ selectedSector: event.target.value })
          }
        >
          <option value="">All Sectors</option>
          {sectors.map((sector) => (
            <option key={sector.name} value={sector.name}>
              {sector.name.charAt(0).toUpperCase() + sector.name.slice(1)}
            </option>
          ))}
        </select>
      </label>

      <label className="text-xs font-medium text-gray-400">
        Ministry / entity
        <select
          className={`${controlClass} mt-1.5`}
          value={selectedMinistry}
          onChange={(event) =>
            onFilterChange({ selectedMinistry: event.target.value })
          }
        >
          <option value="">All Ministries</option>
          {ministries.slice(0, 20).map((ministry) => (
            <option key={ministry.name} value={ministry.name}>
              {ministry.name}
            </option>
          ))}
        </select>
      </label>

      <label className="text-xs font-medium text-gray-400">
        Minimum score: <span className="text-indigo-200">{minScore}</span>
        <input
          className="mt-3 block w-full accent-indigo-400"
          type="range"
          min={0}
          max={100}
          step={1}
          value={minScore}
          onChange={(event) =>
            onFilterChange({ minScore: Number(event.target.value) })
          }
        />
        <span className="mt-1 flex justify-between text-[10px] text-gray-500">
          <span>0</span>
          <span>100</span>
        </span>
      </label>

      <label className="text-xs font-medium text-gray-400">
        Search tenders
        <input
          className={`${controlClass} mt-1.5`}
          type="search"
          placeholder="Search by title..."
          value={search}
          onChange={(event) => onFilterChange({ search: event.target.value })}
        />
      </label>

      <label className="flex min-h-11 items-center gap-3 self-end rounded-lg border border-white/10 px-3 py-2.5 text-sm text-gray-300">
        <input
          className="h-4 w-4 accent-amber-400"
          type="checkbox"
          checked={includeIllustrative}
          onChange={(event) =>
            onFilterChange({ includeIllustrative: event.target.checked })
          }
        />
        Include illustrative
      </label>
    </section>
  )
}
