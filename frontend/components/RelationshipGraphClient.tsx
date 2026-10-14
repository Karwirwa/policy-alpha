'use client'

import dynamic from 'next/dynamic'
import React from 'react'
import { ReactFlowProvider } from 'reactflow'

const Lazy = dynamic(() => import('./RelationshipGraph'), { ssr: false })

export default function RelationshipGraphClient() {
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => setMounted(true), [])

  if (!mounted) return <div className="h-96 flex items-center justify-center text-gray-500">Loading graph...</div>

  return (
    <ReactFlowProvider>
      <Lazy />
    </ReactFlowProvider>
  )
}
