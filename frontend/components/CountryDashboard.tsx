'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, AreaChart, Area, CartesianGrid, BarChart, Bar } from 'recharts'
import Header from './Header'
import { motion } from 'framer-motion'

export default function CountryDashboard({ country }: { country: string }) {
  const { data, isLoading, error } = useQuery<any>({ queryKey: ['country', country], queryFn: () => fetcher(`/api/v1/countries/${encodeURIComponent(country)}`) })
  const { data: evidence = [], isLoading: evidenceLoading } = useQuery<any[]>({
    queryKey: ['countryEvidence', country],
    queryFn: () => fetcher(`/api/v1/evidence/list?country=${encodeURIComponent(country)}&limit=50`),
  })

  if (isLoading) return <div className="p-4"><div className="h-6 bg-gray-800 rounded w-1/3 animate-pulse mb-3" /><div className="h-4 bg-gray-800 rounded w-full animate-pulse" /></div>
  if (error) return <div className="p-4 text-red-400">Error loading country data</div>
  if (!data) return <div className="p-4 text-gray-400">No data</div>

  const ministries = data.top_ministries ?? data.largest_ministries ?? []
  const projects = data.largest_projects ?? []
  const companies = data.most_active_companies ?? data.top_companies ?? []
  const documents = evidence.filter((item: any) => item.document_id).slice(0, 12)

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Country</div>
          <div className="text-xl font-semibold mt-2">{data.country.name}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Opportunity Score</div>
          <div className="text-xl font-semibold mt-2">{Math.round(data.opportunity_score ?? 0)}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Recent Documents</div>
          <div className="text-xl font-semibold mt-2">{data.evidence_count ?? evidence.length}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Top Companies</div>
          <div className="text-xl font-semibold mt-2">{companies.length}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg lg:col-span-2">
          <h4 className="font-medium mb-2">Evidence Timeline</h4>
          {data.evidence_timeline && data.evidence_timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data.evidence_timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f1724" />
                <XAxis dataKey="month" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#60a5fa" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No evidence timeline available</div>
          )}
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Procurement Timeline</h4>
          {data.procurement_timeline && data.procurement_timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data.procurement_timeline}>
                <defs>
                  <linearGradient id="colorP" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#fb923c" fill="url(#colorP)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No procurement timeline data</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Largest Ministries</h4>
          <ul className="text-sm text-gray-200 space-y-2">
            {ministries.length > 0 ? ministries.map((m: any) => (
              <li key={m.agency_id ?? m.id} className="flex justify-between"><span>{m.name}</span><span className="text-gray-400">{m.evidence_count ?? ''}</span></li>
            )) : <li className="text-gray-400">No ministries found</li>}
          </ul>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Largest Projects</h4>
          <ul className="text-sm text-gray-200 space-y-2">
            {projects.length > 0 ? projects.map((p: any) => (
              <li key={p.project_id ?? p.id} className="flex justify-between"><span>{p.name}</span><span className="text-gray-400">{p.evidence_count ?? ''}</span></li>
            )) : <li className="text-gray-400">No projects found</li>}
          </ul>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Top Companies</h4>
          <ul className="text-sm text-gray-200 space-y-2">
            {companies.length > 0 ? companies.map((c: any) => (
              <li key={c.company_id ?? c.id} className="flex justify-between"><a href={`/company/${c.company_id ?? c.id}`} className="text-indigo-300 hover:underline">{c.name ?? c.company_id ?? c.id}</a><span className="text-gray-400">{c.score != null ? Math.round(c.score) : ''}</span></li>
            )) : <li className="text-gray-400">No top companies</li>}
          </ul>
        </div>
      </div>

      <div className="card-glass p-4 rounded-lg mb-6">
        <h4 className="font-medium mb-2">Recent Government Documents</h4>
        <ul className="text-sm text-gray-200 space-y-2">
          {evidenceLoading ? <li className="text-gray-400">Loading evidence...</li> : documents.length > 0 ? documents.map((d: any) => (
            <li key={d.id}><a href={d.source_reference} target="_blank" rel="noreferrer" className="text-indigo-300 hover:underline">{d.title}</a></li>
          )) : <li className="text-gray-400">No recent documents</li>}
        </ul>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Map — Projects</h4>
          <div className="h-60 bg-gradient-to-b from-gray-800 to-gray-900 flex items-center justify-center text-gray-500">Map placeholder (projects)</div>
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Economic Indicators</h4>
          {data.economic_indicators && data.economic_indicators.length > 0 ? (
            <ul>{data.economic_indicators.map((ei: any, idx: number) => (<li key={idx}>{ei.name}: {ei.value}</li>))}</ul>
          ) : (
            <div className="text-gray-400">No economic indicators available</div>
          )}
        </div>
      </div>

    </div>
  )
}
