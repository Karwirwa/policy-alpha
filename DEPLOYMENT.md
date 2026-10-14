## Quick Start (Free Tier)

1. Push this branch to GitHub.
2. In Render, create a **New Web Service**, connect the repository, and select branch `agents/milestone-6-evidence-intelligence-engine`.
3. Render auto-reads `render.yaml` and builds the Docker image.
4. Copy the service URL (for example, `https://policy-alpha-backend.onrender.com`).
5. In Vercel, create a **New Project**, import the same repository, and set the root directory to `frontend`.
6. Set `NEXT_PUBLIC_API_URL=https://<render-url>/api/v1`.
7. Deploy, then visit `https://<vercel-url>/kenya`.

### After First Deploy

- Test the API: `curl https://<render-url>/api/v1/kenya/opportunities`
- If the response is empty, open Render Shell and run the Kenya crawl command below.
- Verify the frontend by opening `https://<vercel-url>/kenya`.

## Prerequisites

- GitHub account
- Render account
- Vercel account

## Step 1: Push the branch to GitHub

Push `agents/milestone-6-evidence-intelligence-engine` to the GitHub repository.

## Step 2: Deploy the backend on Render

1. Create a **New Web Service** and connect the GitHub repository.
2. Select branch `agents/milestone-6-evidence-intelligence-engine`.
3. Set the root directory to the repository root; `render.yaml` points to the backend Dockerfile and build context.
4. Render will read the root `render.yaml` and configure the Docker service.
5. Wait for the build and deployment to finish, then copy the service URL.

## Persistence — Free Tier Behavior

Policy Alpha is deployed on Render's free tier. This means:
- The container restarts after 15 minutes of inactivity.
- The SQLite database resets on each restart.
- Illustrative Kenya demo data is auto-seeded on startup (`DEMO_SEED_ENABLED=true`).
- Live Kenya tenders must be re-crawled after each restart via the admin endpoint or the Render shell.

### Trigger a Fresh Kenya Crawl After Restart

Open the Render Shell for your service and run:

```text
python -c "from app.services.crawler import CrawlerManager; from app.db.database import get_db; db=next(get_db()); print(CrawlerManager(db).run_country('KEN'))"
```

### Upgrading to Persistent Data

When ready for real users, two options:
1. Upgrade to Render Starter ($7/mo) and add a persistent disk.
2. Migrate to Supabase Postgres (free tier, persistent).

## Step 3: Deploy the frontend on Vercel

1. Create a **New Project** and import the GitHub repository.
2. Set the root directory to `frontend`.
3. Confirm the detected framework is Next.js.
4. Add this environment variable, replacing `<render-url>` with the backend URL copied from Render:

   ```text
   NEXT_PUBLIC_API_URL=https://<render-url>/api/v1
   ```

5. Deploy the project.

## Step 4: Verify

Visit `https://<vercel-url>/kenya`. The Kenya opportunities page should show opportunities returned by the Render backend.

## Step 5: Trigger a Kenya crawl remotely

Open the Render service shell and run:

```sh
python -c "from app.services.crawler import CrawlerManager; from app.db.database import get_db; db=next(get_db()); print(CrawlerManager(db).run_country('KEN'))"
```

## Troubleshooting

- **CORS errors:** Check that the backend CORS configuration includes the Vercel origin regex `https://.*\.vercel\.app`.
- **404 responses from the API:** Confirm `NEXT_PUBLIC_API_URL` is set in Vercel to the backend URL ending in `/api/v1`, with no trailing slash. Redeploy after changing environment variables.
