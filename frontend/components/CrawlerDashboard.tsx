'use client'

import React, { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, AreaChart, Area, CartesianGrid, BarChart, Bar } from 'recharts'
import { motion } from 'framer-motion'

export default function CrawlerDashboard() {
  const [countryFilter, setCountryFilter] = useState<string | null>(null)

  // Core metrics: crawler metrics, pipeline jobs, stats and history
  const { data: metrics, isLoading: loadingMetrics, error: metricsError } = useQuery<any>({ queryKey: ['crawlerMetrics'], queryFn: () => fetcher('/api/v1/crawler/metrics'), refetchInterval: 15000 })
  const { data: jobsData, isLoading: loadingJobs, error: jobsError } = useQuery<any>({ queryKey: ['pipelineJobs'], queryFn: () => fetcher('/api/v1/pipeline/jobs'), refetchInterval: 15000 })
  const { data: countries, isLoading: loadingCountries } = useQuery<any>({ queryKey: ['countries'], queryFn: () => fetcher('/api/v1/countries') })
  const { data: stats, isLoading: loadingStats } = useQuery<any>({ queryKey: ['stats'], queryFn: () => fetcher('/api/v1/stats') })
  const { data: crawlHistory } = useQuery<any>({ queryKey: ['crawlHistory'], queryFn: () => fetcher('/api/v1/crawler/history'), refetchInterval: 30000 })

  const isLoading = loadingMetrics || loadingJobs || loadingCountries || loadingStats
  const error = metricsError || jobsError

  const jobs = jobsData?.jobs || []
  const recentJobs = jobs.slice(0, 50)

  // Activity data must be memoized before any conditional return.
  const activityFeed = useMemo(() => {
    const feed: any[] = []
    const runList: any[] = (crawlHistory && (crawlHistory as any).runs && Array.isArray((crawlHistory as any).runs)) ? (crawlHistory as any).runs : []
    runList.slice(0, 50).forEach((r: any) => {
      feed.push({ ts: r.start_time || new Date().toISOString(), type: 'crawl', text: `${r.country_code} crawl ${r.status}`, meta: r })
    })
    recentJobs.forEach((j: any) => {
      feed.push({ ts: j.start_time || new Date().toISOString(), type: 'job', text: `Job ${j.id} ${j.status} stage=${j.stage}`, meta: j })
    })
    return feed.sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime()).slice(0, 200)
  }, [crawlHistory, recentJobs])

  if (isLoading) return <div className="p-6">Loading live operations...</div>
  if (error) return <div className="p-6 text-red-400">Error loading live operations: {String(error)}</div>
  if (!metrics || !jobsData) return <div className="p-6 text-gray-400">No operational data available</div>

  // compute derived metrics
  const filteredCrawlErrors = (metrics.errors?.crawl_errors || []).filter((r: any) => (countryFilter ? (r.country_code || '').toLowerCase() === countryFilter.toLowerCase() : true))
  const filteredPipelineErrors = (metrics.errors?.pipeline_errors || []).filter((e: any) => true)

  // progress percent heuristic: safe fallback when documents_today missing
  const progressPct = metrics && metrics.documents_today ? Math.round(Math.min(100, ((metrics.documents_processed_today || 0) / Math.max(1, metrics.documents_today)) * 100)) : 0

  // queue size
  const queueSize = metrics?.pipeline?.pending_jobs || 0

  // average processing time (compute from completed jobs)
  const completedJobs = jobs.filter((j: any) => j.status === 'completed' && j.start_time && j.end_time)
  const avgProcessingMs = completedJobs.length
    ? Math.round(completedJobs.reduce((acc: number, j: any) => acc + (new Date(j.end_time).getTime() - new Date(j.start_time).getTime()), 0) / completedJobs.length)
    : 0
  const avgProcessingSec = Math.round(avgProcessingMs / 1000)

  // processing speed: docs per hour (use metrics.timeline_docs sum)
  const docsLast24 = (metrics?.timeline_docs || []).reduce((acc: number, v: any) => acc + (v.count || 0), 0)
  const processingSpeedPerHour = Math.round(docsLast24 / 24)

  // top KPIs
  const kpis = [
    { label: 'Documents Downloaded (today)', value: metrics.documents_today },
    { label: 'Evidence Extracted (today)', value: metrics.evidence_today },
    { label: 'Relationships Created (today)', value: metrics.relationships_today },
    { label: 'Companies Found (today)', value: metrics.companies_today },
    { label: 'Projects Found (today)', value: metrics.projects_today },
    { label: 'Opportunity Scores Generated', value: stats?.total_opportunities ?? 0 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold">Live Operations Center</h3>
        <div className="flex items-center gap-3">
          <select
            value={countryFilter ?? ''}
            onChange={(e) => setCountryFilter(e.target.value || null)}
            className="bg-gray-900 text-sm px-3 py-2 rounded"
          >
            <option value="">All countries</option>
            {countries.map((c: any) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {kpis.map((k) => (
          <motion.div key={k.label} layout className="card-glass p-4 rounded-lg">
            <div className="text-sm text-gray-300">{k.label}</div>
            <div className="text-2xl font-semibold mt-2">{k.value}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div layout className="card-glass p-4 rounded-lg col-span-2">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium">Processing Timeline</h4>
            <div className="text-sm text-gray-400">Avg time: {avgProcessingSec}s</div>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={metrics.timeline_docs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f1724" />
                <XAxis dataKey="hour" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#60a5fa" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4">
            <h5 className="text-sm text-gray-400 mb-2">Processing Queue (recent)</h5>
            <div className="space-y-2 max-h-48 overflow-auto">
              {recentJobs.map((j: any) => (
                <div key={j.id} className="flex items-center justify-between bg-gray-900/40 p-2 rounded">
                  <div>
                    <div className="text-sm">Job {j.id} • {j.stage}</div>
                    <div className="text-xs text-gray-400">{j.document_id}</div>
                  </div>
                  <div className="text-sm">{j.status}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div layout className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Activity Feed</h4>
          <div className="max-h-[520px] overflow-auto space-y-2">
            {activityFeed.map((a: any, idx: number) => (
              <div key={idx} className="p-2 rounded bg-gray-900/40">
                <div className="text-xs text-gray-400">{new Date(a.ts).toLocaleString()}</div>
                <div className="text-sm">{a.text}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div layout className="card-glass p-4 rounded-lg col-span-2">
          <h4 className="font-medium mb-2">Pipeline Health</h4>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="text-sm text-gray-400 mb-1">Success rate (24h)</div>
              <div className="w-full bg-gray-800 rounded h-4 overflow-hidden">
                <div className="h-4 bg-green-500" style={{ width: `${metrics.pipeline.success_rate}%` }} />
              </div>
            </div>
            <div className="w-48">
              <div className="text-sm text-gray-400">Queue Size</div>
              <div className="text-2xl font-semibold">{queueSize}</div>
            </div>
          </div>

          <div className="mt-4">
            <h5 className="text-sm text-gray-400 mb-2">Recent Errors</h5>
            <ul className="max-h-40 overflow-auto text-xs text-red-400 space-y-2">
              {filteredCrawlErrors.slice(0,8).map((e:any)=> (
                <li key={e.uuid}>{e.country_code} • {e.status} • {String(e.errors)}</li>
              ))}
              {filteredPipelineErrors.slice(0,8).map((e:any, i:number)=> (
                <li key={i}>Job {e.id ?? 'N/A'} • {String(e.error)}</li>
              ))}
            </ul>
          </div>
        </motion.div>

        <motion.div layout className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Crawler Health</h4>
          <div className="space-y-2">
            {(metrics.current_run ? [metrics.current_run] : []).map((r:any)=> (
              <div key={r.uuid} className="p-2 bg-gray-900/40 rounded">
                <div className="text-sm">Country: {r.country_code}</div>
                <div className="text-xs text-gray-400">Status: {r.status}</div>
                <div className="text-xs text-gray-400">Documents found: {r.documents_found}</div>
              </div>
            ))}
            <div className="mt-2 text-sm text-gray-400">Processing speed: {processingSpeedPerHour} docs/hr</div>
            <div className="text-sm text-gray-400">Avg processing: {avgProcessingSec}s</div>
            <div className="text-sm text-gray-400">Retries: {metrics.pipeline?.failures ?? 0}</div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
