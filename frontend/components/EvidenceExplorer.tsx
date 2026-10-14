'use client'

import React, { useMemo, useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { format } from 'date-fns'
import ReactFlow, { MiniMap, Controls, Background, Node, Edge } from 'reactflow'
import 'reactflow/dist/style.css'

export default function EvidenceExplorer() {
  const [keyword, setKeyword] = useState('')
  const [country, setCountry] = useState('kenya')
  const [agency, setAgency] = useState('')
  const [company, setCompany] = useState('')
  const [project, setProject] = useState('')
  const [tender, setTender] = useState('')
  const [confidenceMin, setConfidenceMin] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [limit, setLimit] = useState(50)
  const [offset, setOffset] = useState(0)
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null)

  const params = useMemo(() => {
    const p: Record<string, any> = { limit, offset }
    if (keyword) p.keyword = keyword
    if (country) p.country = country
    if (agency) p.agency = agency
    if (company) p.company = company
    if (project) p.project = project
    if (tender) p.tender = tender
    if (confidenceMin) p.confidence_min = parseFloat(confidenceMin)
    if (startDate) p.start_date = startDate
    if (endDate) p.end_date = endDate
    return p
  }, [keyword, country, agency, company, project, tender, confidenceMin, startDate, endDate, limit, offset])

  const qs = useMemo(() => {
    const esc = encodeURIComponent
    const parts: string[] = []
    for (const k in params) {
      parts.push(`${esc(k)}=${esc(String(params[k]))}`)
    }
    return parts.length ? '?' + parts.join('&') : ''
  }, [params])

  const { data, isLoading, error } = useQuery<any[]>({ queryKey: ['evidenceList', qs], queryFn: () => fetcher(`/api/v1/evidence/list${qs}`) })

  const onSearch = useCallback((e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); setOffset(0); }, [])

  const nodes: Node[] = useMemo(() => {
    if (!selectedDoc) return []
    const n: Node[] = []
    const centerId = `doc-${selectedDoc.id}`
    n.push({ id: centerId, position: { x: 0, y: 0 }, data: { label: selectedDoc.title }, style: { background: '#111827', color: '#fff', padding: 8, borderRadius: 6 } })
    let idx = 0
    const types = ['company_id','agency_id','project_id','procurement_id','budget_id']
    types.forEach((t, i) => {
      const val = selectedDoc[t]
      if (val) {
        const nid = `${t}-${val}`
        n.push({ id: nid, position: { x: 250, y: i * 60 - 120 }, data: { label: `${t.replace('_id','')}: ${val}` }, style: { background: '#0ea5a9', color: '#fff', padding: 6, borderRadius: 6 } })
        idx += 1
      }
    })
    if (selectedDoc.extracted_keywords && selectedDoc.extracted_keywords.length) {
      const kId = 'keywords'
      n.push({ id: kId, position: { x: -250, y: 0 }, data: { label: `keywords: ${selectedDoc.extracted_keywords.slice(0,6).join(', ')}` }, style: { background: '#a78bfa', color: '#fff', padding: 6, borderRadius: 6 } })
    }
    return n
  }, [selectedDoc])

  const edges: Edge[] = useMemo(() => {
    if (!selectedDoc) return []
    const e: Edge[] = []
    const centerId = `doc-${selectedDoc.id}`
    const types = ['company_id','agency_id','project_id','procurement_id','budget_id']
    types.forEach((t) => {
      const val = selectedDoc[t]
      if (val) {
        const nid = `${t}-${val}`
        e.push({ id: `e-${centerId}-${nid}`, source: centerId, target: nid, animated: true, style: { stroke: '#64748b' } })
      }
    })
    if (selectedDoc.extracted_keywords && selectedDoc.extracted_keywords.length) {
      e.push({ id: `e-${centerId}-keywords`, source: centerId, target: 'keywords', animated: false, style: { stroke: '#a78bfa' } })
    }
    return e
  }, [selectedDoc])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <form onSubmit={onSearch} className="flex gap-2 mb-4">
          <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Search keyword" className="flex-1 bg-transparent border border-gray-700 px-3 py-2 rounded" />
          <input value={country} onChange={(e) => setCountry(e.target.value)} placeholder="Country" className="w-40 bg-transparent border border-gray-700 px-2 py-2 rounded" />
          <input value={agency} onChange={(e) => setAgency(e.target.value)} placeholder="Agency" className="w-40 bg-transparent border border-gray-700 px-2 py-2 rounded" />
          <button className="px-3 py-2 bg-indigo-600 rounded">Search</button>
        </form>

        <div className="card-glass p-4 rounded-lg">
          <h4 className="font-medium mb-2">Results</h4>
          {isLoading ? (
            <div className="space-y-2">
              <div className="h-4 bg-gray-800 rounded w-1/2 animate-pulse" />
              <div className="h-4 bg-gray-800 rounded w-3/4 animate-pulse" />
            </div>
          ) : error ? (
            <div className="text-red-400">Error loading evidence</div>
          ) : data && data.length > 0 ? (
            <ul className="space-y-3">
              {data.map((d: any) => (
                <li key={d.id} className="py-3 border-b border-gray-700 flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-sm">{d.title}</div>
                    <div className="text-xs text-gray-400">{d.source_reference} • {d.publication_date ? format(new Date(d.publication_date), 'yyyy-MM-dd') : ''} • Confidence: {Math.round(d.evidence_strength*100)/100}</div>
                    <div className="text-sm mt-2 text-gray-200">{d.summary?.slice(0, 300)}{d.summary && d.summary.length > 300 ? '...' : ''}</div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <button className="px-3 py-1 bg-indigo-600 rounded" onClick={() => setSelectedDoc(d)}>Open</button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-400">No results</div>
          )}

          <div className="mt-4 flex items-center justify-between">
            <div>
              <button className="px-2 py-1 bg-gray-800 rounded mr-2" onClick={() => setOffset(Math.max(0, offset - limit))}>Prev</button>
              <button className="px-2 py-1 bg-gray-800 rounded" onClick={() => setOffset(offset + limit)}>Next</button>
            </div>
            <div className="text-sm text-gray-400">Showing {data ? data.length : 0} results</div>
          </div>
        </div>
      </div>

      <aside className="card-glass p-4 rounded-lg">
        <h4 className="font-medium">Document Details</h4>
        {!selectedDoc ? (
          <div className="text-gray-400 mt-3">Select a document to view metadata and relationships</div>
        ) : (
          <div className="mt-3 text-sm text-gray-200">
            <div className="font-medium">{selectedDoc.title}</div>
            <div className="text-xs text-gray-400">Source: <a className="text-indigo-300 hover:underline" href={selectedDoc.source_reference} target="_blank" rel="noreferrer">{selectedDoc.source_reference}</a></div>
            <div className="mt-2">Publication: {selectedDoc.publication_date ? format(new Date(selectedDoc.publication_date), 'yyyy-MM-dd') : 'N/A'}</div>
            <div className="mt-2">Confidence: {selectedDoc.evidence_strength}</div>

            <div className="mt-3">
              <div className="font-medium">Summary</div>
              <div className="text-sm mt-2 text-gray-200">{selectedDoc.summary}</div>
            </div>

            <div className="mt-3">
              <div className="font-medium">Connected Entities</div>
              <ul className="text-sm mt-2 text-gray-200 space-y-1">
                {selectedDoc.company_id && <li>Company: <a className="text-indigo-300 hover:underline" href={`/company/${selectedDoc.company_id}`}>{selectedDoc.company_id}</a></li>}
                {selectedDoc.agency_id && <li>Agency: <a className="text-indigo-300 hover:underline" href={`/graph/agency/${selectedDoc.agency_id}`}>{selectedDoc.agency_id}</a></li>}
                {selectedDoc.project_id && <li>Project: <a className="text-indigo-300 hover:underline" href={`/graph/project/${selectedDoc.project_id}`}>{selectedDoc.project_id}</a></li>}
                {selectedDoc.procurement_id && <li>Tender: <a className="text-indigo-300 hover:underline" href={`/graph/budget/${selectedDoc.procurement_id}`}>{selectedDoc.procurement_id}</a></li>}
              </ul>
            </div>

            <div className="mt-3">
              <div className="font-medium">Supporting Evidence</div>
              <ul className="text-sm mt-2 text-gray-200 space-y-1">
                {/* For now, supporting evidence are other evidence items for same document */}
                {selectedDoc.document_id ? (
                  // This simple call fetches other evidence for the same document
                  <DocEvidenceList documentId={selectedDoc.document_id} />
                ) : (
                  <li className="text-gray-400">No supporting evidence</li>
                )}
              </ul>
            </div>

            <div className="mt-4">
              <div className="font-medium">Relationship Graph</div>
              <div className="h-48 mt-2">
                {selectedDoc ? (
                  <ReactFlow nodes={nodes} edges={edges} fitView>
                    <MiniMap />
                    <Controls />
                    <Background />
                  </ReactFlow>
                ) : (
                  <div className="text-gray-400">No graph</div>
                )}
              </div>
            </div>
          </div>
        )}
      </aside>
    </div>
  )
}

function DocEvidenceList({ documentId }: { documentId: string }) {
  const { data, isLoading } = useQuery<any[]>({ queryKey: ['docEvidence', documentId], queryFn: () => fetcher(`/api/v1/evidence/document/${encodeURIComponent(documentId)}`) })
  if (isLoading) return <li className="text-gray-400">Loading supporting evidence...</li>
  if (!data || data.length === 0) return <li className="text-gray-400">No supporting evidence</li>
  return (
    <>
      {data.map((d: any) => (
        <li key={d.id}><a className="text-indigo-300 hover:underline" href={d.source_reference} target="_blank" rel="noreferrer">{d.title}</a></li>
      ))}
    </>
  )
}
