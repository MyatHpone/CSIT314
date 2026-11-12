# Renovation Match Platform — CSIT314

A role-based web application for matching renovation customers with interior designers. It follows the Boundary-Controller-Entity (BCE) design pattern (same skeleton as the SDM Online Fundraising System): a Python/Flask backend split into `boundary/`, `controller/` and `entity/`, SQLite persistence, server-rendered HTML in `frontend/`, and a small JSON API.

## Requirements

- Python 3.10 or newer
- `pip`
- Internet connection on first page load for Bootstrap CSS/JS CDN (the core application does not require a third-party API).

## Run on macOS

```bash
cd renovation_match_platform/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m app.main
```

Open `http://127.0.0.1:5000`.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| User Admin | `admin` | `Admin123!` |
| Interior Designer | `designer` | `Design123!` |
| Customer | `customer` | `Customer123!` |
| Platform Manager | `manager` | `Manager123!` |

Change these demo credentials and set a strong `SECRET_KEY` before any deployment. Seed data is created automatically the first time the database is initialized. It creates 100 companies, 100 categories and 100 projects, plus four demo accounts. The SQLite file is `backend/renovation_match.db`.

To reset demo data, stop the server and remove `renovation_match.db`; the next launch will recreate it.



## Project structure (BCE)

```
renovation_match_platform/
├── backend/
│   ├── app/
│   │   ├── boundary/     # Flask routes, one file per use case (Boundary layer)
│   │   ├── controller/   # Business rules, one file per use case (Controller layer)
│   │   ├── entity/       # Domain classes + SQL (Entity layer)
│   │   ├── services/     # database.py (SQLite + seed), auth.py, validators.py, results.py
│   │   ├── config.py
│   │   └── main.py       # Flask app factory / entry point
│   ├── tests/            # unittest suite (incl. BCE layering checks)
│   └── requirements.txt
├── frontend/
│   ├── templates/        # Jinja HTML pages
│   └── static/           # CSS
└── README.md
```


## Main screens

Dashboard, Login, User Accounts, User Profile, Profile Search, Companies, Projects, Project Details, My Shortlist, Compare, Project Analytics, Categories, and Reports.

## JSON endpoints

- `GET /api/health` — health check
- `GET /api/projects?q=modern&status=CURRENT` — project search
- `GET /api/projects/<id>` — project details
- `GET /api/metrics` — aggregate counts (requires an authorized role)

## Test-driven development

Run tests:

```bash
cd backend
python -m unittest discover -s tests -v
```

## CI/CD

This project uses **GitHub Actions** to automatically run all 17 unit tests on every push to the `main` branch.

View the workflow: `.github/workflows/ci.yml`

---
