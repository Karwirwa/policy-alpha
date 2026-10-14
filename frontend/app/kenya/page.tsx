'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import Header from '../../components/Header'
import FilterBar, {
  type OpportunityFilters,
} from '../../components/kenya/FilterBar'
import OpportunityCard from '../../components/kenya/OpportunityCard'
import SectorSummary from '../../components/kenya/SectorSummary'
import {
  getKenyaMinistries,
  getKenyaOpportunities,
  getKenyaSectors,
  type Ministry,
  type Opportunity,
  type Sector,
} from '../../lib/api/kenya'

const initialFilters: OpportunityFilters = {
  selectedSector: '',
  selectedMinistry: '',
  minScore: 0,
  search: '',
  includeIllustrative: false,
}

export default function KenyaOpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [total, setTotal] = useState(0)
  const [sectors, setSectors] = useState<Sector[]>([])
  const [ministries, setMinistries] = useState<Ministry[]>([])
  const [filters, setFilters] = useState(initialFilters)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryKey, setRetryKey] = useState(0)

  const loadData = useCallback(async (includeIllustrative: boolean) => {
    setLoading(true)
    setError(null)
    try {
      const [opportunityData, sectorData, ministryData] = await Promise.all([
        getKenyaOpportunities(1000, includeIllustrative),
        getKenyaSectors(),
        getKenyaMinistries(),
      ])
      return { opportunityData, sectorData, ministryData }
    } catch (requestError) {
      throw requestError
    }
  }, [])

  useEffect(() => {
    let active = true
    loadData(filters.includeIllustrative)
      .then(({ opportunityData, sectorData, ministryData }) => {
        if (!active) return
        setOpportunities(opportunityData.opportunities)
        setTotal(opportunityData.total)
        setSectors(sectorData.sectors)
        setMinistries(ministryData.ministries)
      })
      .catch((requestError: unknown) => {
        if (!active) return
        setError(
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load Kenya opportunities.',
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [filters.includeIllustrative, loadData, retryKey])

  const filteredOpportunities = useMemo(() => {
    const normalizedSearch = filters.search.trim().toLowerCase()
    return opportunities.filter((opportunity) => {
      if (
        filters.selectedSector &&
        opportunity.sector !== filters.selectedSector
      ) {
        return false
      }
      if (
        filters.selectedMinistry &&
        opportunity.ministry !== filters.selectedMinistry
      ) {
        return false
      }
      if (opportunity.score < filters.minScore) return false
      if (
        normalizedSearch &&
        !opportunity.title.toLowerCase().includes(normalizedSearch)
      ) {
        return false
      }
      return true
    })
  }, [filters, opportunities])

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mb-8 border-b border-white/10 pb-6">
        <p className="text-sm font-medium uppercase tracking-[0.18em] text-indigo-300">
          Kenya intelligence
        </p>
        <div className="mt-2 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Kenya opportunities
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-400">
              Ranked procurement signals from Kenya public tenders, grouped by
              sector and procuring entity.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
            <div className="text-2xl font-semibold tabular-nums text-white">
              {total}
            </div>
            <div className="text-xs text-gray-400">opportunities</div>
          </div>
        </div>
      </div>

      <div className="space-y-7">
        <SectorSummary
          sectors={sectors}
          selectedSector={filters.selectedSector}
          onSelect={(selectedSector) =>
            setFilters((current) => ({ ...current, selectedSector }))
          }
        />

        <FilterBar
          sectors={sectors}
          ministries={ministries}
          selectedSector={filters.selectedSector}
          selectedMinistry={filters.selectedMinistry}
          minScore={filters.minScore}
          search={filters.search}
          includeIllustrative={filters.includeIllustrative}
          onFilterChange={(changes) =>
            setFilters((current) => ({ ...current, ...changes }))
          }
        />

        <section aria-label="Ranked Kenya opportunities">
          <div className="mb-4 flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
            <h2 className="text-lg font-semibold text-white">
              Ranked opportunities
            </h2>
            <p className="text-sm text-gray-400">
              Showing {filteredOpportunities.length} of {opportunities.length}
              {filters.includeIllustrative ? ' (including illustrative)' : ''}
            </p>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
              {[0, 1, 2, 3, 4, 5].map((item) => (
                <div
                  key={item}
                  className="h-56 animate-pulse rounded-2xl border border-white/10 bg-white/[0.03]"
                />
              ))}
            </div>
          ) : error ? (
            <div
              className="rounded-2xl border border-red-400/20 bg-red-400/5 p-6"
              role="alert"
            >
              <p className="font-medium text-red-300">
                Could not load Kenya opportunities
              </p>
              <p className="mt-1 text-sm text-gray-400">{error}</p>
              <button
                type="button"
                onClick={() => setRetryKey((key) => key + 1)}
                className="mt-4 rounded-lg bg-red-400/10 px-4 py-2 text-sm font-medium text-red-200 transition hover:bg-red-400/20"
              >
                Retry
              </button>
            </div>
          ) : filteredOpportunities.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredOpportunities.map((opportunity) => (
                <OpportunityCard
                  key={opportunity.evidence_id}
                  opportunity={opportunity}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-white/[0.025] px-6 py-12 text-center">
              <p className="font-medium text-gray-200">No matching tenders</p>
              <p className="mt-1 text-sm text-gray-500">
                Try changing or clearing your filters.
              </p>
            </div>
          )}
        </section>
      </div>
    </main>
  )
}
