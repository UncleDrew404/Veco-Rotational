# VECO frontend

Nuxt 4 frontend for the VECO interruption calendar API. The application uses
JavaScript, Vite, Tailwind CSS, and Pinia.

The initial schedule is loaded with Nuxt `useFetch()` for SSR. Pinia stores the
result and uses `$fetch()` when the user refreshes the schedule.

## Local development

1. Copy `.env.example` to `.env` if the Django API uses a different origin.
2. Start Django at `http://127.0.0.1:8080` with `python manage.py runserver`.
3. Install and start Nuxt:

```powershell
npm install
npm run dev
```

The frontend is available at `http://localhost:3000`.
