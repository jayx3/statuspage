# ClearStatus

A very simple Statuspage-style app: create projects, track component status, post incidents,
and share a public status page. Built with Flask + MongoDB + Bootstrap 5.

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# make sure MongoDB is running locally, then:
export SECRET_KEY="change-me"
export MONGO_URI="mongodb://localhost:27017/statuspage"

python app.py
```

Visit http://localhost:5000, register an account, and create your first project.

## Deployment (Ubuntu + Gunicorn + Nginx)

1. Copy the project to the server and install dependencies inside a virtualenv.
2. Set `SECRET_KEY` and `MONGO_URI` as environment variables (e.g. in a systemd unit file).
3. Run the app with Gunicorn:
   ```bash
   gunicorn -w 3 -b 127.0.0.1:8000 app:app
   ```
4. Point Nginx at `127.0.0.1:8000` as a reverse proxy, serving `/static` directly for
   better performance.

## Project Structure

- `app.py` — routes for the dashboard, projects, components, incidents, and the public status page
- `auth.py` — registration, login, logout (Flask-Login)
- `models.py` — MongoDB helper functions (no ORM)
- `config.py` — configuration via environment variables
- `templates/` — Jinja2 templates, Bootstrap 5 for styling
- `static/` — CSS and vanilla JS
