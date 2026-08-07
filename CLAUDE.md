# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FixFast: a repair-shop management app (clientes, órdenes de reparación, pagos, caja, dashboard) for a Spanish-speaking business. Backend and frontend code, comments, and commit messages are in Spanish — match that when editing existing files. Two independent projects sharing this repo:

- `backend/` — FastAPI + SQLAlchemy, talks to a Supabase Postgres database.
- `frontend/` — Vue 3 (Composition API, `<script setup>`) + Vite + Pinia + Tailwind v4.

There is no test suite and no linter config in either project. Don't invent test/lint commands.

## Commands

### Backend (from `backend/`)
```bash
python3 -m venv .venv && source .venv/bin/activate   # first time
pip install -r requirements.txt
cp .env.example .env          # then fill DATABASE_URL / SUPABASE_URL / keys
uvicorn app.main:app --reload --port 8010   # run dev server (matches vite proxy target below)
python -m app.init_db         # create tables from SQLAlchemy models (run once against Supabase)
python3 -m py_compile app/main.py app/database.py app/init_db.py app/auth/dependencies.py app/models/*.py app/routes/*.py app/schemas/*.py   # quick syntax check, used in lieu of a linter
```
After `init_db.py` creates `public.usuarios` for the first time, run `backend/sql/supabase_trigger.sql` once in the Supabase SQL editor (adds the `auth.users` FK and the trigger that mirrors new signups into `usuarios`).

### Frontend (from `frontend/`)
```bash
npm install
npm run dev        # Vite dev server; proxies /api -> http://127.0.0.1:8010 (see vite.config.js)
npm run build
npm run preview
cp .env.example .env   # VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
```

## Architecture

### Auth
Supabase Auth issues the JWTs; this app never handles passwords itself.
- Frontend: `frontend/src/lib/supabaseClient.js` wraps `@supabase/supabase-js`; `stores/auth.js` hydrates the persisted session on boot and calls `supabase.auth.signInWithPassword`. `api/http.js`'s axios interceptor attaches `Authorization: Bearer <access_token>` from the current Supabase session on every request and force-logs-out on a 401 response.
- Backend: `backend/app/auth/dependencies.py`'s `get_current_user` verifies the incoming JWT against the project's public JWKS (`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`, cached in-memory for an hour) — not a static HS256 secret — then loads the matching row from `public.usuarios` by `sub`. Almost every router declares `dependencies=[Depends(get_current_user)]` at the `APIRouter` level.
- `public_routes.py` (`/publico/seguimiento`) is the one deliberately unauthenticated router — it's the endpoint the end customer hits from `/seguimiento` to track their own repair by order code + phone number, so it must not require a session.
- `public.usuarios` rows are created automatically by a Postgres trigger mirroring `auth.users` (see `backend/sql/supabase_trigger.sql`), not by app code. `usuarios.id` intentionally has no SQLAlchemy `ForeignKey` to `auth.users` (that schema is outside `Base.metadata`); the real FK constraint is added by the SQL script directly.

### Backend request flow
`routes/*_routes.py` (FastAPI `APIRouter`s, included in `app/main.py`) → SQLAlchemy models in `models/*.py`, using the `get_db` session dependency from `app/database.py`. Pydantic schemas in `schemas/*_schema.py` define request/response shapes. There's no separate service/repository layer except `services/dashboard_service.py`, which holds all dashboard aggregation logic (SQL-side `SUM`/`COUNT`/`GROUP BY`, not Python-side aggregation, to avoid loading full tables).

### Estado (order status) vocabulary — single source of truth split across two files
`Orden.estado` is a free-text column (never migrated to a Postgres enum, to avoid breaking historical rows), but the canonical vocabulary, ordering, colors, and legacy-string matching live in exactly one place per side:
- Backend: `backend/app/core/estados.py` (`ESTADOS`, `resolve_estado_key`).
- Frontend: `frontend/src/constants/estados.js` (mirrors the backend by hand — key/label/color must stay identical).

Only 4 states exist by design: `pendiente`, `listo`, `entregado`, `cancelado` (older states like "Diagnóstico"/"Esperando repuesto"/"En reparación" were intentionally dropped from the flow). Legacy/variant strings resolve to a canonical key via substring matching against an alias table in both files — if you add or rename a state, update both files together.

### Órdenes (repair tickets)
- `numero_orden` (customer-facing tracking code, e.g. `FF-000123`) is generated *after* insert in `orden_routes.py` because it embeds the DB-assigned `id`.
- Changing `Orden.estado` via `PUT /ordenes/{id}` writes a row to `historial_estados` (only when the value actually changed) — this trace powers dashboard metrics like time-in-status and "days without movement". Don't bypass this route to change status directly.
- Deleting an order manually cascades `pagos` and `historial_estados` first (no DB-level `ON DELETE CASCADE` on those FKs).

### Money movements: two related but distinct concepts
- `pagos` (`Pago` model) — payments tied to a specific `orden_id`.
- `movimientos_caja` (`MovimientoCaja` model) — general cash-register entries (`tipo` in/out, `categoria`, `metodo_pago`), not tied to an order. This is what backs the `caja`/`finanzas` view.
- Frontend-side, "Pagos" and "Otros ingresos" (counter sales like parts/accessories) were merged into a single `PagosView.vue` screen; `/ingresos` and `/finanzas` routes now redirect (`ordenes`→`pagos`, `finanzas`→`caja`) — see `router/index.js`. Keep old links working by redirecting, don't delete these route aliases.

### API conventions (frontend `src/api/`)
- `api/http.js` is the single axios instance (baseURL from `VITE_API_URL`, defaults to `/api`); all other `api/*.js` files build on it.
- List/create endpoints are defined in FastAPI with a trailing slash (`/clientes/`); detail endpoints (`/clientes/{id}`) are not. Calling a detail endpoint *with* a trailing slash triggers a 307 redirect that some proxies (Vite dev proxy included) mis-resolve into HTML instead of JSON — always match the trailing-slash convention already used in `api/resources.js` when adding endpoints.
- Vite dev proxy forwards `/api/*` to `http://127.0.0.1:8010` (see `vite.config.js`), stripping the `/api` prefix — run the backend on port 8010 in dev, or update both `vite.config.js` and the deployed `VITE_API_URL`.

### Deployment
Backend and frontend ship as separate Docker images (`backend/Dockerfile`, `frontend/Dockerfile`) — frontend's is a multi-stage build (Vite build → static `nginx:alpine` serving `dist/`, `nginx.conf` rewrites all non-file routes to `index.html` for Vue Router history mode). `frontend/netlify.toml` is an alternative static-hosting path (Netlify build + SPA redirect), not used together with the Docker/nginx path. The database is always Supabase Postgres (Session Pooler connection string, not Transaction Pooler — SQLAlchemy's persistent connection pool needs prepared-statement support the Transaction Pooler doesn't reliably give).
