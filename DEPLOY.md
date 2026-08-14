# Deployment guide (free tier: Render + Supabase + Tigris + Vercel)

Stack:
- **Render** – backend (FastAPI; conversions run in-process, no worker, no Redis)
- **Supabase** – PostgreSQL
- **Tigris** – S3-compatible object storage (browser presigned uploads work out of the box)
- **Vercel** – frontend (React/Vite)

```
Vercel (React) → Render API → Python conversion → Tigris (files) + Supabase (jobs)
```

Limits enforced in `backend/app/core/config.py`:
- `MAX_CONCURRENT_JOBS=2` (returns `429 Too many conversions` when busy)
- `MAX_FILE_SIZE_MB=25` (rejected with a clear error)
- Guest files expire after 24h; expired files + guests older than 7 days are purged hourly by an in-process background task (no cron/worker needed)

## 1. Supabase (database)

1. Create a free project at supabase.com (e.g. `your-converter`).
2. Database → Connection string → **Session pooler / direct** (port `5432`, NOT transaction pooler `6543` — Alembic DDL fails on the transaction pooler).
3. Use the `postgresql://postgres.<ref>:<password>@...:5432/postgres` URL (plain `postgresql://...` is fine — the backend auto-normalizes it to the psycopg driver).
4. No manual table creation needed: the backend Docker image runs `alembic upgrade head` before uvicorn starts (free-plan safe). Look for `Running upgrade -> 0001` in the deploy logs. If your password contains `#`, keep it URL-encoded as `%23`.

## 2. Tigris (object storage)

1. Create a free account at tigrisdata.com.
2. Create a bucket (e.g. `converter-files`).
3. In project settings copy:
   - Access key / secret key → `S3_ACCESS_KEY` / `S3_SECRET_KEY`
   - Endpoint → `https://fly.storage.tigris.dev` (or your project endpoint) → `S3_ENDPOINT`
   - Region → `S3_REGION=auto`

## 3. Render (backend only)

1. Push the repo to GitHub and create a **Blueprint** from `render.yaml` (dashboard → New + → Blueprint). It creates one web service, `universal-converter-api` — no worker service.
2. Set the env vars:
   | Env var | Value |
   |---|---|
   | `DATABASE_URL` | Supabase URL from step 1 |
   | `S3_ENDPOINT` | `https://fly.storage.tigris.dev` |
   | `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Tigris keys |
   | `S3_BUCKET_NAME` | Tigris bucket name |
   | `S3_REGION` | `auto` |
   | `CORS_ORIGINS` | `https://<your-vercel-domain>.vercel.app` |
   | `ADMIN_EMAIL` | your admin email |
   | `ADMIN_PASSWORD` | a strong password (remove after first login if you like) |
3. `SECRET_KEY` + `APP_ENV=production` are set automatically by the blueprint.
4. Deploy. On startup the log shows `Admin bootstrap: created admin (<email>)`, then the API starts.
5. URL: `https://universal-converter-api.onrender.com`.

Note: the image installs `libreoffice` (docx → pdf) and `ghostscript` (PDF processing) — first deploy takes a few minutes.

## 4. Vercel (frontend)

1. Import the repo, root directory `frontend`, framework preset Vite.
2. Either set build env var `VITE_API_URL=https://universal-converter-api.onrender.com/api/v1`, **or** add `frontend/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/api/v1/:path*", "destination": "https://universal-converter-api.onrender.com/api/v1/:path*" }
  ]
}
```

   With the rewrite, leave `VITE_API_URL` unset (frontend falls back to same-origin `/api/v1`). Either way `CORS_ORIGINS` on Render must include the Vercel domain.

## 5. Verify

- `GET https://<render>/api/v1/health` → healthy
- `POST https://<render>/api/v1/auth/guest` → returns `access_token`
- Open `https://<vercel-domain>/` → converter loads immediately with a guest session (no login page), conversion runs inline and completes in seconds
- Open `https://<vercel-domain>/admin-login` (hidden route — no link in the UI) → sign in with `ADMIN_EMAIL`/`ADMIN_PASSWORD` → Admin panel

## Local development

`docker compose up` uses MinIO + Postgres (no Redis, no worker). For local admin bootstrap, set `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `backend/.env` — the backend creates the admin on startup (same as production).