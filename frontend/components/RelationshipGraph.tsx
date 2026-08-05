'use client'

import React, { useCallback, useEffect, useMemo, useState } from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
  Connection,
  Edge,
  Node,
  MarkerType,
  useReactFlow,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { useQuery } from '@tanstack/react-query'
import { fetcher } from '../lib/fetcher'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import { motion } from 'framer-motion'
import { IconBuilding, IconGovernment, IconBox, IconFileText, IconStack } from 'lucide-react'

type GraphResponse = {
  entity: { entity_type: string; entity_id: string; entity_name: string }
  connections: Array<any>
}

const NODE_COLORS: Record<string, string> = {
  company: '#a78bfa',
  agency: '#60a5fa',
  project: '#34d399',
  budget: '#fbbf24',
  tender: '#fb7185',
  evidence: '#64748b',
}

function nodeColor(ntype: string) {
  return NODE_COLORS[ntype] || '#94a3b8'
}

function NodeIcon({ type }: { type: string }) {
  switch (type) {
    case 'company':
      return <IconBuilding className="w-5 h-5" />
    case 'agency':
      return <IconGovernment className="w-5 h-5" />
    case 'project':
      return <IconStack className="w-5 h-5" />
    case 'budget':
      return <IconBox className="w-5 h-5" />
    case 'tender':
      return <IconFileText className="w-5 h-5" />
    case 'evidence':
      return <IconFileText className="w-5 h-5" />
    default:
      return <IconBuilding className="w-5 h-5" />
  }
}

export default function RelationshipGraph() {
  const [queryType, setQueryType] = useState<'company' | 'agency' | 'project'>('company')
  const [queryText, setQueryText] = useState('')
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [viewportInitialized, setViewportInitialized] = useState(false)
  const { fitView, setCenter } = useReactFlow()

  const buildGraph = useCallback((data: GraphResponse) => {
    if (!data) return
    const centerId = `focus-${data.entity.entity_type}-${data.entity.entity_id}`
    const created: Record<string, boolean> = {}
    const newNodes: Node[] = []
    const newEdges: Edge[] = []

    // add focus node
    newNodes.push({
      id: centerId,
      position: { x: 0, y: 0 },
      data: { label: data.entity.entity_name, type: data.entity.entity_type, id: data.entity.entity_id },
      style: { background: nodeColor(data.entity.entity_type), color: '#fff', padding: 8, borderRadius: 8 },
    })
    created[centerId] = true

    let angle = 0
    const radius = 220
    const per = Math.max(1, data.connections.length)

    data.connections.forEach((conn: any, idx: number) => {
      const otherId = `${conn.other_entity_type}-${conn.other_entity_id}`
      const nodeId = otherId
      if (!created[nodeId]) {
        const x = Math.cos((angle / per) * Math.PI * 2) * radius
        const y = Math.sin((angle / per) * Math.PI * 2) * radius
        angle += 1
        newNodes.push({
          id: nodeId,
          position: { x, y },
          data: { label: conn.other_entity_name, type: conn.other_entity_type, id: conn.other_entity_id, evidence: conn.evidence },
          style: { background: nodeColor(conn.other_entity_type), color: '#fff', padding: 8, borderRadius: 8 },
        })
        created[nodeId] = true
      }

      // edge between center and other
      newEdges.push({
        id: `e-${centerId}-${nodeId}-${idx}`,
        source: centerId,
        target: nodeId,
        animated: true,
        markerEnd: { type: MarkerType.Arrow, color: nodeColor(conn.other_entity_type) },
        style: { stroke: nodeColor(conn.other_entity_type), strokeWidth: 1.5 },
        data: { relationship: conn.relationship_type, confidence: conn.confidence, evidence: conn.evidence },
      })

      // if evidence attached, create evidence node and connect
      if (conn.evidence) {
        const evId = `evidence-${conn.evidence.id}`
        if (!created[evId]) {
          const x = Math.cos((angle / per) * Math.PI * 2) * (radius + 120)
          const y = Math.sin((angle / per) * Math.PI * 2) * (radius + 120)
          newNodes.push({
            id: evId,
            position: { x, y },
            data: { label: conn.evidence.title, type: 'evidence', id: conn.evidence.id, source: conn.evidence.source_reference },
            style: { background: nodeColor('evidence'), color: '#fff', padding: 6, borderRadius: 6 },
          })
          created[evId] = true
        }
        newEdges.push({
          id: `e-${nodeId}-${evId}`,
          source: nodeId,
          target: evId,
          animated: false,
          style: { stroke: nodeColor('evidence'), strokeWidth: 1 },
        })
      }
    })

    setNodes(newNodes)
    setEdges(newEdges)

    // center view after a short delay to ensure nodes mounted
    setTimeout(() => {
      try {
        fitView({ padding: 0.2 })
        setViewportInitialized(true)
      } catch (e) {
        // ignore
      }
    }, 200)
  }, [fitView, setCenter, setViewportInitialized])

  const fetchGraph = useCallback(async () => {
    if (!queryText) return
    const path = `/api/v1/graph/${queryType}/${encodeURIComponent(queryText)}`
    const data = await fetcher<GraphResponse>(path)
    buildGraph(data)
  }, [queryType, queryText, buildGraph])

  // handle node click
  const onNodeClick = useCallback((event: any, node: Node) => {
    setSelectedNode(node)
    // center on node
    try {
      setCenter(node.position.x, node.position.y, { zoom: 1.2 })
    } catch (e) {}
  }, [setCenter])

  // search handlers
  const onSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    fetchGraph().catch(() => {})
  }, [fetchGraph])

  // helper to pan to node
  const panToNode = useCallback((nodeId: string) => {
    const n = nodes.find((x) => x.id === nodeId)
    if (n) {
      try {
        setCenter(n.position.x, n.position.y, { zoom: 1.2 })
      } catch (e) {}
    }
  }, [nodes, setCenter])

  // build initial empty graph
  useEffect(() => {
    // nothing
  }, [])

  return (
    <div className="w-full h-[70vh] lg:h-[80vh] rounded-lg overflow-hidden">
      <div className="flex items-center gap-3 mb-3">
        <form onSubmit={onSubmit} className="flex items-center gap-2 w-full">
          <div className="flex items-center gap-2">
            <select value={queryType} onChange={(e) => setQueryType(e.target.value as any)} className="bg-transparent border border-gray-700 px-2 py-1 rounded">
              <option value="company">Company</option>
              <option value="agency">Agency</option>
              <option value="project">Project</option>
            </select>
          </div>

          <input
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder={`Search ${queryType} name...`}
            className="flex-1 bg-transparent border border-gray-700 px-3 py-2 rounded"
          />

          <button type="submit" className="px-3 py-2 bg-indigo-600 rounded">Search</button>
        </form>

        <div className="ml-2">
          <button className="px-3 py-2 bg-gray-800 rounded" onClick={() => { setNodes([]); setEdges([]); setSelectedNode(null); }}>Clear</button>
        </div>
      </div>

      <div className="flex gap-4 h-full">
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
            defaultViewport={{ x: 0, y: 0, zoom: 1 }}
            minZoom={0.2}
            maxZoom={2.5}
            panOnDrag
            zoomOnScroll
          >
            <MiniMap nodeColor={(n) => nodeColor((n.data as any)?.type)} />
            <Controls />
            <Background color="#0b1220" gap={16} />
          </ReactFlow>
        </div>

        <aside className="w-80">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card-glass p-4 rounded-lg h-full overflow-auto">
            <h4 className="font-semibold">Node Details</h4>
            {selectedNode ? (
              <div className="mt-3 text-sm text-gray-200">
                <div className="font-medium">{(selectedNode.data as any)?.label}</div>
                <div className="text-xs text-gray-400 mt-1">Type: {(selectedNode.data as any)?.type}</div>
                <div className="text-xs text-gray-400">ID: {(selectedNode.data as any)?.id}</div>

                <div className="mt-3">
                  <div className="font-medium">Connected Evidence</div>
                  <ul className="mt-2 space-y-2 text-xs text-gray-300">
                    {edges
                      .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                      .map((e) => (e.data && (e.data as any).evidence ? (e.data as any).evidence : null))
                      .filter(Boolean)
                      .map((ev: any) => (
                        <li key={ev.id}>
                          <a className="text-indigo-300 hover:underline" target="_blank" rel="noreferrer" href={ev.source_reference || '#'}>
                            {ev.title}
                          </a>
                        </li>
                      ))}
                  </ul>
                </div>

                <div className="mt-3">
                  <div className="font-medium">Connected Nodes</div>
                  <ul className="mt-2 space-y-2 text-xs text-gray-300">
                    {edges
                      .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                      .map((e) => ({ other: e.source === selectedNode.id ? e.target : e.source, rel: (e.data as any)?.relationship }))
                      .map((o) => (
                        <li key={o.other}>
                          <button onClick={() => panToNode(o.other)} className="text-left w-full text-indigo-200 hover:underline">
                            {o.other} • {o.rel}
                          </button>
                        </li>
                      ))}
                  </ul>
                </div>

                <div className="mt-4">
                  <button className="px-3 py-2 bg-indigo-600 rounded" onClick={() => { if ((selectedNode.data as any)?.type === 'company') { window.location.href = `/company/${(selectedNode.data as any)?.label}` } }}>
                    Open Company Page
                  </button>
                </div>
              </div>
            ) : (
              <div className="mt-3 text-sm text-gray-400">Click a node to see details</div>
            )}
          </motion.div>
        </aside>
      </div>
    </div>
  )
}
