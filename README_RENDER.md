# Render Deployment Package

This folder is ready to upload to a GitHub repository and deploy on Render.

## Render settings

The included `render.yaml` configures:

- Runtime: Python
- Plan: Free
- Build command: `pip install -r web_app/requirements.txt`
- Start command: `gunicorn web_app.app:app`
- Health check: `/`

During Blueprint creation, enter a value for:

`CIRCUIT_TUTOR_LECTURER_PIN`

For the current demonstration, you can use:

`1234`

## Important free-plan limitation

The app currently uses SQLite for the competitive leaderboard. Render's free
web-service filesystem is temporary, so leaderboard records can reset after a
restart or redeployment. The public website itself will still work. Move the
leaderboard to PostgreSQL later for permanent online records.
