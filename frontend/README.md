Policy Alpha Frontend (Phase 1)

This frontend is a Next.js 16 App Router project scaffolded to integrate with the Policy Alpha FastAPI backend.

Structure

- app/: Next.js App Router pages and layouts
- components/: Reusable UI components
- lib/: Utilities (API client, providers)
- styles/: Global styles and Tailwind config

Running locally

1. cd frontend
2. npm install
3. Set environment variable NEXT_PUBLIC_API_BASE to the backend base URL (e.g. http://127.0.0.1:8000)
4. npm run dev

Phase 1 delivered

- Next.js 16 App Router scaffold
- TypeScript configured
- Tailwind CSS configured (dark mode default)
- Basic global layout and header
- Landing page and Dashboard page
- Placeholder routes for other pages
- API fetch helper (lib/fetcher.ts)

Remaining work before Phase 2

- Implement Dashboard UI components and wire real API calls
- Add TanStack Query provider to wrap the app
- Install UI libraries (shadcn/ui), charting libs, React Flow
- Build reusable components, skeletons, error states
- Implement authentication if required

Design notes

Keep dark-mode-first, glassmorphism where appropriate, and a premium SaaS-like spacing and typography.
