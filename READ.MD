# VECO Interruptions

A full-stack application that retrieves Visayan Electric interruption data and
displays it as a searchable schedule. The Django REST Framework backend reads
the live VECO calendar dataset, while the Nuxt frontend presents scheduled and
rotational brownout records with text, category, and date filters.

## Project structure

```text
veco-rotational/
├── veco-be/   Django REST Framework API
└── veco-fe/   Nuxt 4 frontend
```

## Technology stack

### Backend

- Python and Django
- Django REST Framework
- `requests`, `feedparser`, and Beautiful Soup
- `django-cors-headers`
- `python-dotenv`

### Frontend

- Nuxt 4 and Vue 3
- Vite
- Tailwind CSS
- Pinia
- ESLint

## Environment files

Local `.env` files are ignored by Git. Commit the `.env.example` templates,
but never commit real credentials or production configuration.

### Backend environment

Copy the backend template:

```powershell
Copy-Item veco-be/.env.example veco-be/.env
```

The backend uses:

```dotenv
SECRET_KEY=replace-with-a-long-random-secret-key
VECO_FEED_URL=*************************
VECO_CALENDAR_DATA_URL=**************************************
VECO_CALENDAR_PAGE_URL=************************************************
CORS_ALLOWED_ORIGINS=**********************************************************
```

Generate a unique, unpredictable `SECRET_KEY` before deploying the backend.
`CORS_ALLOWED_ORIGINS` accepts a comma-separated list without trailing slashes.

### Frontend environment

Copy the frontend template:

```powershell
Copy-Item veco-fe/.env.example veco-fe/.env
```

The frontend uses:

```dotenv
NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

Variables prefixed with `NUXT_PUBLIC_` are included in the browser bundle and
must never contain secrets.

## Backend setup

From the repository root:

```powershell
Set-Location veco-be
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py check
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000` by default.

## Frontend setup

In another terminal, from the repository root:

```powershell
Set-Location veco-fe
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:3000`. The schedule page is available at
`http://localhost:3000/schedule`.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/v1/interruptions/` | Return every event in the live VECO calendar dataset. |
| `GET` | `/api/v1/interruptions/?date=today` | Return events covering today in `Asia/Manila`. |
| `GET` | `/api/v1/interruptions/?date=YYYY-MM-DD` | Return events covering a selected date. |
| `GET` | `/api/v1/interruptions/latest/` | Return the newest service-interruption article from the VECO RSS feed. |

The collection endpoint is public, read-only, and stateless. It returns an
empty `data` list when no events match a valid date. Invalid dates return `400`,
and upstream retrieval or parsing failures return `502`.

## Data flow

```text
VECO publishes or updates its interruption calendar
        ↓
Django retrieves and validates the live calendar dataset
        ↓
Django REST Framework returns structured JSON
        ↓
Nuxt loads the collection with useFetch()
        ↓
Pinia stores, refreshes, and filters the schedule
```

The `latest` compatibility endpoint follows the RSS entry to its VECO article
and parses the article schedule. The main collection endpoint uses the direct
calendar dataset so updates published on VECO's calendar can appear without
waiting for a new blog entry.

## Validation

Run backend checks and tests:

```powershell
Set-Location veco-be
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Run frontend linting and production build:

```powershell
Set-Location veco-fe
npm run lint
npm run build
```

## Before pushing

Confirm that local environment files are ignored and not tracked:

```powershell
git check-ignore -v veco-be/.env veco-fe/.env
git ls-files veco-be/.env veco-fe/.env
```

The first command should show matching `.gitignore` rules. The second command
should return no paths.
