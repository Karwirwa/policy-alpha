'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, AreaChart, Area, CartesianGrid } from 'recharts'

export default function CrawlerDashboard() {
  const { data, isLoading, error, refetch } = useQuery(['crawlerMetrics'], () => fetcher('/api/v1/crawler/metrics'), { refetchInterval: 30000 })

  if (isLoading) return <div className="p-4">Loading crawler metrics...</div>
  if (error) return <div className="p-4 text-red-400">Error loading crawler metrics</div>
  if (!data) return <div className="p-4 text-gray-400">No data</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Crawler Dashboard</h3>
        <div className="text-sm text-gray-400">Last updated: {new Date().toLocaleString()}</div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Crawler Running</div>
          <div className="text-2xl font-semibold mt-2">{data.crawler_running ? 'Yes' : 'No'}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Current Country</div>
          <div className="text-2xl font-semibold mt-2">{data.current_run?.country_code ?? '—'}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Documents discovered (today)</div>
          <div className="text-2xl font-semibold mt-2">{data.documents_today}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Evidence extracted (today)</div>
          <div className="text-2xl font-semibold mt-2">{data.evidence_today}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Discoveries</h4>
          <div className="text-sm text-gray-300">Companies discovered: <strong className="text-white">{data.companies_today}</strong></div>
          <div className="text-sm text-gray-300">Projects discovered: <strong className="text-white">{data.projects_today}</strong></div>
          <div className="text-sm text-gray-300">Relationships created: <strong className="text-white">{data.relationships_today}</strong></div>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Pipeline Health</h4>
          <div className="text-sm text-gray-300">Success rate (24h): <strong>{Math.round(data.pipeline.success_rate)}%</strong></div>
          <div className="text-sm text-gray-300">Total jobs (24h): <strong>{data.pipeline.total_jobs_last24h}</strong></div>
          <div className="text-sm text-gray-300">Pending jobs: <strong>{data.pipeline.pending_jobs}</strong></div>
          <div className="mt-2">
            <div className="w-full bg-gray-800 rounded h-3 overflow-hidden">
              <div className="h-3 bg-green-500" style={{ width: `${data.pipeline.success_rate}%` }} />
            </div>
          </div>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Errors</h4>
          <div className="text-sm text-red-400">Crawl errors: {data.errors.crawl_errors.length}</div>
          <div className="text-sm text-red-400">Pipeline errors: {data.errors.pipeline_errors.length}</div>
          <div className="mt-2 text-xs text-gray-400">Recent crawl errors</div>
          <ul className="mt-2 text-xs text-gray-200 max-h-40 overflow-auto">
            {data.errors.crawl_errors.slice(0,5).map((e:any)=> (
              <li key={e.uuid} className="mb-2">{e.country_code} • {e.status} • {JSON.stringify(e.errors)}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Documents discovered (last 24h)</h4>
          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer>
              <LineChart data={data.timeline_docs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f1724" />
                <XAxis dataKey="hour" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#60a5fa" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Evidence extracted (last 24h)</h4>
          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer>
              <AreaChart data={data.timeline_evidence}>
                <defs>
                  <linearGradient id="gEv" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#10b981" fill="url(#gEv)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card-glass p-4 rounded-lg">
        <h4 className="font-medium mb-2">Processing Queue</h4>
        <div className="text-sm text-gray-300">Pending jobs: <strong>{data.pipeline.pending_jobs}</strong></div>
        <div className="text-sm text-gray-300">Success rate: <strong>{Math.round(data.pipeline.success_rate)}%</strong></div>

        <div className="mt-3">
          <div className="w-full bg-gray-800 rounded h-3 overflow-hidden">
            <div className="h-3 bg-blue-500" style={{ width: `${data.pipeline.success_rate}%` }} />
          </div>
        </div>

        <div className="mt-4 text-xs text-gray-400">Recent pipeline errors</div>
        <ul className="mt-2 text-xs text-gray-200 max-h-48 overflow-auto">
          {data.errors.pipeline_errors.slice(0,10).map((e:any)=> (
            <li key={e.id} className="mb-2">{e.stage} • {String(e.error)}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
