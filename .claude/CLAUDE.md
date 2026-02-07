# Celestial Explorer — Backend

Django REST API serving a celestial object catalog (stars, planets, galaxies) for the Celestial Explorer frontend.

## Project Structure

- `config/` — Django project package (settings, urls, wsgi, asgi)
- `apps/gaia/` — Single domain app: models, serializers, views, filters, admin, ingestion
- `apps/gaia/clients/` — External API clients (ESA Gaia TAP, NASA Exoplanet Archive)
- `apps/gaia/management/commands/` — Ingestion commands (`ingest_stars`, `ingest_planets`, `ingest_galaxies`)

## Architecture

- **Frontend reads from DB only** — no proxy/passthrough endpoints
- **Ingestion is a separate background service** — management commands pull from external APIs and write to PostgreSQL
- All API endpoints are read-only (`AllowAny`, no auth)
- Pagination: `{ count, next, previous, results }` — matches frontend's `PaginatedResponse<T>`

## Tech Stack

- Django 5.1, Django REST Framework, django-filter, django-cors-headers
- PostgreSQL (`celestial_explorer` DB)
- psycopg 3, requests

## Settings

- `config.settings.base` — shared config
- `config.settings.local` — dev overrides (DEBUG, CORS for localhost:5173)
- `DJANGO_SETTINGS_MODULE=config.settings` defaults to local via `__init__.py`

## API

All endpoints under `/api/v1/`:
- `/stars/`, `/stars/<id>/`, `/stars/stats/`
- `/planets/`, `/planets/<id>/`, `/planets/stats/`
- `/galaxies/`, `/galaxies/<id>/`, `/galaxies/stats/`

## Conventions

- App name in Django config: `apps.gaia` (dotted path)
- Imports use `apps.gaia.*` for absolute, or relative within the app
- Models inherit from `CelestialObject` abstract base (shared fields: name, catalog_id, RA/Dec, distance, cartesian coords)
- Two serializers per model: `ListSerializer` (compact) and `DetailSerializer` (full)
