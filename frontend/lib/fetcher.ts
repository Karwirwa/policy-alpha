/**
 * Typed fetch helper that uses NEXT_PUBLIC_API_URL as the API base URL.
 *
 * Example:
 * import fetcher from 'frontend/lib/fetcher'
 * const data = await fetcher<MyType>('/items')
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export async function fetcher<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const url = path.startsWith('http')
    ? path
    : `${API_BASE.replace(/\/$/, '')}/${path.replace(/^\/api\/v1\/?/, '').replace(/^\//, '')}`

  const mergedHeaders = {
    'Content-Type': 'application/json',
    ...(init && (init as any).headers),
  }
  const res = await fetch(url, { ...init, headers: mergedHeaders })
  if (!res.ok) {
    const contentType = res.headers.get('content-type') || ''
    let errorBody: any = null
    try {
      errorBody = contentType.includes('application/json') ? await res.json() : await res.text()
    } catch (_) {
      // ignore parse errors
    }
    const err = new Error(`Request failed with status ${res.status}`) as any
    err.status = res.status
    err.info = errorBody
    throw err
  }

  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return res.json()
  return (await res.text()) as unknown as T
}

export default fetcher
