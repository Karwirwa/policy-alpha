import { fetcher } from '../fetcher'

export type Opportunity = {
  evidence_id: number
  document_id: string
  title: string
  sector: string
  ministry: string
  deadline: string | null
  score: number
  source_url: string
  verification_status: string
  summary_excerpt: string
}

export type Sector = {
  name: string
  count: number
  avg_score: number
}

export type Ministry = {
  name: string
  count: number
  total_score: number
}

export async function getKenyaOpportunities(
  limit = 20,
  includeIllustrative = false,
): Promise<{ opportunities: Opportunity[]; total: number }> {
  const query = new URLSearchParams({
    limit: String(limit),
    include_illustrative: String(includeIllustrative),
  })
  return fetcher(`/api/v1/kenya/opportunities?${query.toString()}`)
}

export function getKenyaSectors(): Promise<{ sectors: Sector[] }> {
  return fetcher('/api/v1/kenya/sectors')
}

export function getKenyaMinistries(): Promise<{ ministries: Ministry[] }> {
  return fetcher('/api/v1/kenya/ministries')
}

export function getKenyaUpcoming(days = 30): Promise<{ upcoming: Opportunity[] }> {
  const query = new URLSearchParams({ days: String(days) })
  return fetcher(`/api/v1/kenya/upcoming?${query.toString()}`)
}
