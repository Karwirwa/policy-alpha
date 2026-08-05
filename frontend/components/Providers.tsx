'use client'

import React from 'react'
import { QueryProvider } from '../lib/QueryProvider'

export default function Providers({ children }: { children: React.ReactNode }) {
  return <QueryProvider>{children}</QueryProvider>
}
