# Deployment guide (free tier: Render + Supabase + Tigris + Vercel)

Stack:
- **Render** – backend (FastAPI, `render.yaml` web service) + worker (Celery/Beat, `render.yaml` worker service)
- **Supabase** – PostgreSQL
- **Tigris** – S3-compatible object storage (browser presigned uploads work out of the box)
- **Vercel** – frontend (React/Vite)

## 1. Supabase (database)

1. Create a free project at supabase.com (e.g. `your-converter`).
2. Database → Connection string → **Session pooler / direct** (port `5432`, NOT transaction pooler `6543` — Alembic DDL fails on the transaction pooler).
3. Use the `postgresql://postgres.<ref>:<password>@...:5432/postgres` URL (plain `postgresql://...` is fine — the backend auto-normalizes it to the psycopg driver).
4. You do **not** need to create tables: the backend Docker image runs `alembic upgrade head` automatically before uvicorn starts (free-plan safe — no pre-deploy command needed). You'll see `Running upgrade -> 0001, initial schema` in the deploy logs.

## 2. Tigris (object storage)

1. Create a free account at tigrisdata.com.
2. Create a bucket (e.g. `converter-files`).
3. In the project settings copy:
   - Access key / secret key → `S3_ACCESS_KEY` / `S3_SECRET_KEY`
   - Endpoint → use `https://fly.storage.tigris.dev` (or your project endpoint) → `S3_ENDPOINT`
   - Region → `S3_REGION=auto`

## 3. Render (backend + worker)

1. Push the repo to GitHub and create a **Blueprint** from `render.yaml` (dashboard → New + → Blueprint).
2. For the **web service** (`universal-converter-api`) set:
   | Env var | Value |
   |---|---|
   | `DATABASE_URL` | Supabase URL from step 1 |
   | `REDIS_URL` | a Redis provider (e.g. Upstash or Render Redis): `rediss://...` |
   | `S3_ENDPOINT` | `https://fly.storage.tigris.dev` |
   | `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Tigris keys |
   | `S3_BUCKET_NAME` | Tigris bucket name |
   | `S3_REGION` | `auto` |
   | `CORS_ORIGINS` | `https://<your-vercel-domain>.vercel.app` (comma-separated if multiple) |
   | `ADMIN_EMAIL` | your admin email |
   | `ADMIN_PASSWORD` | a strong password (remove after first login if you like) |
3. `SECRET_KEY` + `APP_ENV=production` are set automatically by the blueprint.
4. Deploy. On startup the log should show `Admin bootstrap: created admin (<email>)` and `alembic upgrade head` should have applied `0001_initial`.
5. The **worker service** (`universal-converter-worker`) needs the same `DATABASE_URL`, `REDIS_URL`, `S3_*` values. It builds with the backend code included (backend app is mounted at `/backend`).
6. URL: `https://universal-converter-api.onrender.com` (add `ALWAYS_ON`/`autoscaling` later if you want zero cold starts).

## 4. Vercel (frontend)

1. Import the repo, root directory `frontend`.
2. Framework preset: Vite.
3. Set build env var `VITE_API_URL=https://universal-converter-api.onrender.com/api/v1` (and redeploy if you changed it).
4. Alternatively (no build-time env needed): add a rewrite in `frontend/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/api/v1/:path*", "destination": "https://universal-converter-api.onrender.com/api/v1/:path*" }
  ]
}
```

   In that case leave `VITE_API_URL` unset (frontend falls back to the same-origin `/api/v1`). Either way, `CORS_ORIGINS` on Render must include the Vercel domain.

## 5. Verify

- `GET https://<render>/api/v1/health` → healthy
- `POST https://<render>/api/v1/auth/guest` → returns `access_token`
- Open `https://<vercel-domain>/` → converter loads immediately with a guest session (no login page)
- Open `https://<vercel-domain>/admin-login` (hidden route — no link in the UI) → sign in with `ADMIN_EMAIL`/`ADMIN_PASSWORD` → Admin panel

## Local development

`docker compose up` uses MinIO + Redis + Postgres (see `docker-compose.yml`). For local admin bootstrap, set `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `backend/.env` — the backend creates the admin on startup (same as production).