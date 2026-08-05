'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts'
import { motion } from 'framer-motion'

function KpiCard({ title, value, loading, error }: { title: string; value: any; loading?: boolean; error?: any }) {
  if (loading) return <div className="card-glass p-4 rounded-lg animate-pulse">Loading...</div>
  if (error) return <div className="card-glass p-4 rounded-lg text-red-400">Error</div>
  return (
    <div className="card-glass p-4 rounded-lg">
      <div className="text-sm text-gray-300">{title}</div>
      <div className="text-2xl font-semibold mt-2">{value}</div>
    </div>
  )
}

export default function DashboardMain() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery(['stats'], () => fetcher('/api/v1/stats'))
  const { data: topOp, isLoading: topLoading } = useQuery(['topOpportunities'], () => fetcher('/api/v1/opportunity/top'))
  const { data: latestEvidence, isLoading: evidenceLoading } = useQuery(['latestEvidence'], () => fetcher('/api/v1/evidence/latest'))
  const { data: crawlerStatus, isLoading: crawlerLoading } = useQuery(['crawlerStatus'], () => fetcher('/api/v1/crawler/status'))

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <KpiCard title="Total companies" value={stats?.total_companies ?? '—'} loading={statsLoading} error={statsError} />
          <KpiCard title="Total agencies" value={stats?.total_agencies ?? '—'} loading={statsLoading} error={statsError} />
          <KpiCard title="Total projects" value={stats?.total_projects ?? '—'} loading={statsLoading} error={statsError} />
          <KpiCard title="Total evidence" value={stats?.total_evidence ?? '—'} loading={statsLoading} error={statsError} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="card-glass p-4 rounded-lg lg:col-span-2">
            <h4 className="font-medium mb-2">Opportunity Trends</h4>
            <div style={{ width: '100%', height: 220 }}>
              {statsLoading ? (
                <div className="h-56 animate-pulse bg-gray-800 rounded" />
              ) : stats?.opportunity_trend && stats.opportunity_trend.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={stats.opportunity_trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#0f1724" />
                    <XAxis dataKey="month" stroke="#9aa6b2" />
                    <YAxis stroke="#9aa6b2" />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#60a5fa" strokeWidth={2} dot={{ r: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-400">No opportunity history available</div>
              )}
            </div>
          </div>

          <div className="card-glass p-4 rounded-lg">
            <h4 className="font-medium mb-2">Evidence Growth</h4>
            <div style={{ width: '100%', height: 220 }}>
              {statsLoading ? (
                <div className="h-56 animate-pulse bg-gray-800 rounded" />
              ) : stats?.evidence_growth && stats.evidence_growth.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={stats.evidence_growth}>
                    <defs>
                      <linearGradient id="colorEv" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#34d399" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" stroke="#9aa6b2" />
                    <YAxis stroke="#9aa6b2" />
                    <Tooltip />
                    <Area type="monotone" dataKey="count" stroke="#10b981" fillOpacity={1} fill="url(#colorEv)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-400">No evidence history available</div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card-glass p-4 rounded-lg lg:col-span-2">
            <h4 className="font-medium mb-2">Latest Evidence</h4>
            {evidenceLoading ? (
              <div className="space-y-2">
                <div className="h-4 bg-gray-800 rounded w-3/4 animate-pulse" />
                <div className="h-4 bg-gray-800 rounded w-1/2 animate-pulse" />
              </div>
            ) : latestEvidence && latestEvidence.length > 0 ? (
              <ul className="space-y-3">
                {latestEvidence.slice(0, 10).map((e: any) => (
                  <li key={e.id} className="py-3 border-b border-gray-700">
                    <div className="text-sm font-medium">{e.title}</div>
                    <div className="text-xs text-gray-400 mt-1">{e.source_reference} • {e.publication_date || ''}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-400">No recent evidence</div>
            )}
          </div>

          <div className="card-glass p-4 rounded-lg">
            <h4 className="font-medium mb-2">Top Opportunities</h4>
            {topLoading ? (
              <div className="space-y-2">
                <div className="h-4 bg-gray-800 rounded w-3/4 animate-pulse" />
                <div className="h-4 bg-gray-800 rounded w-1/2 animate-pulse" />
              </div>
            ) : topOp && topOp.length > 0 ? (
              <ol className="list-decimal list-inside text-sm space-y-2">
                {topOp.slice(0, 8).map((t: any) => (
                  <li key={t.company_id} className="flex justify-between">
                    <span>{t.company_id}</span>
                    <span className="font-medium">{Math.round(t.total_score ?? t.score ?? 0)}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <div className="text-gray-400">No opportunities discovered yet</div>
            )}

            <div className="mt-4 text-xs text-gray-400">Crawler: {crawlerLoading ? 'loading' : crawlerStatus?.scheduler_running ? 'running' : 'idle'}</div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
