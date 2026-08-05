'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, BarChart, Bar, Legend } from 'recharts'

export default function PortfolioPanel({ portfolioUuid }: { portfolioUuid: string }) {
  const qc = useQueryClient()
  const { data: portfolios } = useQuery(['portfolios'], () => fetcher('/api/v1/portfolio'))
  const portfolioId = portfolios && portfolios[0] ? portfolios[0].uuid : portfolioUuid

  const { data, isLoading, error } = useQuery(['portfolioOverview', portfolioId], () => fetcher(`/api/v1/portfolio/${encodeURIComponent(portfolioId)}/overview`), { enabled: !!portfolioId })
  const { data: watchlist } = useQuery(['watchlist'], () => fetcher('/api/v1/watchlist'))

  // add company mutation
  const addMutation = useMutation((payload: any) => fetch(`/api/v1/portfolio/${portfolioId}/company`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }), { onSuccess: () => qc.invalidateQueries(['portfolioOverview', portfolioId]) })

  // remove company
  const removeMutation = useMutation((companyId: string) => fetch(`/api/v1/portfolio/${portfolioId}/company/${companyId}`, { method: 'DELETE' }), { onSuccess: () => qc.invalidateQueries(['portfolioOverview', portfolioId]) })

  const [addCompanyId, setAddCompanyId] = useState('')

  if (isLoading) return <div className="p-4">Loading portfolio...</div>
  if (error) return <div className="p-4 text-red-400">Error loading portfolio</div>
  if (!data) return <div className="p-4 text-gray-400">No portfolio data</div>

  const COLORS = ['#60a5fa', '#34d399', '#fbbf24', '#fb7185', '#a78bfa']

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Total invested</div>
          <div className="text-2xl font-semibold mt-2">${Math.round(data.total_invested)}</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Projected return</div>
          <div className="text-2xl font-semibold mt-2">{Math.round(data.projected_return)}%</div>
        </div>
        <div className="card-glass p-4 rounded-lg">
          <div className="text-sm text-gray-300">Government exposure</div>
          <div className="text-2xl font-semibold mt-2">{Math.round(data.government_exposure)}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Country Allocation</h4>
          {data.country_allocation && data.country_allocation.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie dataKey="count" data={data.country_allocation} outerRadius={60} fill="#8884d8" label>
                  {data.country_allocation.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No country allocation data</div>
          )}
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Sector Allocation</h4>
          {data.sector_allocation && data.sector_allocation.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie dataKey="value" data={data.sector_allocation} outerRadius={60} fill="#82ca9d" label>
                  {data.sector_allocation.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No sector allocation data</div>
          )}
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Risk & Opportunity</h4>
          <div className="mb-2">Risk Score: <strong>{Math.round(data.risk_score)}</strong></div>
          <div>Opportunity Score: <strong>{Math.round(data.opportunity_score)}</strong></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Historical Simulations</h4>
          {data.historical_simulations && data.historical_simulations.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={data.historical_simulations}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f1724" />
                <XAxis dataKey="buy_date" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Line type="monotone" dataKey="percent_return" stroke="#60a5fa" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No simulations run yet</div>
          )}
        </div>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Country Allocation (Bar)</h4>
          {data.country_allocation && data.country_allocation.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data.country_allocation}>
                <XAxis dataKey="country_id" stroke="#9aa6b2" />
                <YAxis stroke="#9aa6b2" />
                <Tooltip />
                <Bar dataKey="count" fill="#60a5fa" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-400">No country allocation data</div>
          )}
        </div>
      </div>

      <div className="card-glass p-4 rounded-lg mb-6">
        <h4 className="font-medium mb-2">Watchlist</h4>
        {watchlist && watchlist.length > 0 ? (
          <ul className="text-sm text-gray-200 space-y-2">
            {watchlist.map((w: any) => (
              <li key={w.uuid} className="flex justify-between items-center"><div><a href={`/company/${w.company_id}`} className="text-indigo-300 hover:underline">{w.company_id}</a><div className="text-xs text-gray-400">Priority: {w.priority}</div></div><div><button className="px-2 py-1 bg-red-600 rounded" onClick={() => { fetch(`/api/v1/watchlist/${w.company_id}`, { method: 'DELETE' }).then(() => qc.invalidateQueries(['watchlist'])) }}>Remove</button></div></li>
            ))}
          </ul>
        ) : (
          <div className="text-gray-400">No watchlist items</div>
        )}
      </div>

      <div className="card-glass p-4 rounded-lg mb-6">
        <h4 className="font-medium mb-2">Manage Portfolio</h4>
        <div className="flex gap-2">
          <input className="flex-1 bg-transparent border border-gray-700 px-3 py-2 rounded" placeholder="Company ID to add" value={addCompanyId} onChange={(e) => setAddCompanyId(e.target.value)} />
          <button className="px-3 py-2 bg-indigo-600 rounded" onClick={() => addMutation.mutate({ company_id: addCompanyId, allocation_percent: 10 })}>Add</button>
        </div>

        <div className="mt-4">
          <h5 className="font-medium mb-2">Positions</h5>
          {portfolios && portfolios.length > 0 ? (
            <ul className="text-sm text-gray-200 space-y-2">
              {portfolios.map((p: any) => (
                <li key={p.uuid} className="flex justify-between items-center"><div>{p.name}</div><div><button className="px-2 py-1 bg-red-600 rounded" onClick={() => removeMutation.mutate(p.uuid)}>Remove</button></div></li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-400">No positions</div>
          )}
        </div>
      </div>

    </div>
  )
}
