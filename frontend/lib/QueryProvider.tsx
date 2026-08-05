/**
 * Client-side QueryProvider.
 * Wraps children with a QueryClientProvider and Hydrate for SSR hydration support.
 *
 * Usage (in _app.tsx):
 * <QueryProvider dehydratedState={pageProps.dehydratedState}>{children}</QueryProvider>
 */
'use client'

import React, { useState } from 'react'
import { QueryClient, QueryClientProvider, Hydrate } from '@tanstack/react-query'

type QueryProviderProps = {
  children: React.ReactNode
  dehydratedState?: unknown
}

export function QueryProvider({ children, dehydratedState }: QueryProviderProps) {
  // Create a new QueryClient for each mounted provider to avoid sharing state between renders/requests.
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <Hydrate state={dehydratedState}>{children}</Hydrate>
    </QueryClientProvider>
  )
}

export default QueryProvider
