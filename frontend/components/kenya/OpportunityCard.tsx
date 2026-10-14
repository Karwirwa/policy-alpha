import type { Opportunity } from '../../lib/api/kenya'

type OpportunityCardProps = {
  opportunity: Opportunity
}

const sectorColors: Record<string, string> = {
  water: 'bg-blue-500/15 text-blue-300 ring-blue-400/25',
  roads: 'bg-gray-500/15 text-gray-300 ring-gray-400/25',
  health: 'bg-red-500/15 text-red-300 ring-red-400/25',
  education: 'bg-purple-500/15 text-purple-300 ring-purple-400/25',
  ict: 'bg-cyan-500/15 text-cyan-300 ring-cyan-400/25',
  energy: 'bg-yellow-500/15 text-yellow-300 ring-yellow-400/25',
  construction: 'bg-orange-500/15 text-orange-300 ring-orange-400/25',
  consultancy: 'bg-indigo-500/15 text-indigo-300 ring-indigo-400/25',
  other: 'bg-gray-500/15 text-gray-300 ring-gray-400/25',
}

function verificationStyle(status: string): string {
  if (status === 'verified') return 'bg-emerald-500/15 text-emerald-300'
  if (status === 'illustrative') return 'bg-amber-500/15 text-amber-300'
  return 'bg-gray-500/15 text-gray-300'
}

function formatDeadline(deadline: string): string {
  const date = new Date(deadline)
  if (Number.isNaN(date.getTime())) return deadline
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

export default function OpportunityCard({ opportunity }: OpportunityCardProps) {
  const scoreColor =
    opportunity.score >= 70
      ? 'text-emerald-300'
      : opportunity.score >= 50
        ? 'text-amber-300'
        : 'text-gray-300'
  const sector = opportunity.sector.toLowerCase()

  return (
    <article className="flex h-full flex-col rounded-2xl border border-white/10 bg-white/[0.035] p-5 shadow-lg shadow-black/10 transition duration-200 hover:-translate-y-0.5 hover:border-indigo-400/30 hover:bg-white/[0.055]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h3
            className="min-h-12 overflow-hidden text-base font-semibold leading-6 text-white"
            style={{
              display: '-webkit-box',
              WebkitBoxOrient: 'vertical',
              WebkitLineClamp: 2,
            }}
            title={opportunity.title}
          >
            {opportunity.title}
          </h3>
          <p className="mt-1 truncate text-xs text-gray-400" title={opportunity.ministry}>
            {opportunity.ministry}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <div className={`text-3xl font-bold tabular-nums ${scoreColor}`}>
            {Math.round(opportunity.score)}
          </div>
          <div className="text-[10px] uppercase tracking-wider text-gray-500">Score</div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ring-1 ring-inset ${
            sectorColors[sector] ?? sectorColors.other
          }`}
        >
          {sector}
        </span>
        <span className={`rounded-full px-2.5 py-1 text-xs capitalize ${verificationStyle(opportunity.verification_status)}`}>
          {opportunity.verification_status}
        </span>
      </div>

      {opportunity.deadline && (
        <p className="mt-4 text-sm text-amber-300">
          Closes: {formatDeadline(opportunity.deadline)}
        </p>
      )}

      {opportunity.summary_excerpt && (
        <p className="mt-3 line-clamp-3 text-sm leading-5 text-gray-400">
          {opportunity.summary_excerpt}
        </p>
      )}

      <div className="mt-auto flex items-end justify-between gap-3 pt-5">
        <span className="min-w-0 truncate text-xs text-gray-500" title={opportunity.document_id}>
          Ref: {opportunity.document_id}
        </span>
        {opportunity.source_url && (
          <a
            className="shrink-0 text-sm font-medium text-indigo-300 transition hover:text-indigo-200"
            href={opportunity.source_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            View Source <span aria-hidden="true">→</span>
          </a>
        )}
      </div>
    </article>
  )
}
