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

**Layer rules** (enforced by `ArchitectureTests`):

- **Boundary** handles HTTP only (request, session, flash, render, redirect). Each boundary file has a class (for example `CreateUserAccountBoundary` with `display_page`, `submit_form`, `show_success`, `show_error`) and a thin Flask route that calls it. It calls controllers and never imports entities or the database.
- **Controller** holds validation and business rules and returns `(success, result)` tuples, like the SDM controllers. No Flask code.
- **Entity** owns the data and parameterised SQL. It never imports controllers or boundaries.

| Use case (stories) | Boundary | Controller | Entity |
|---|---|---|---|
| Login / logout (1, 2, 13, 14, 30, 31, 47, 48) | `login_user_account`, `logout_user_account` | `LoginUserAccountController`, `LogoutUserAccountController` | `UserAccount`, `ActivityEvent` |
| Dashboard | `view_dashboard` | `ViewDashboardController` | `Report`, `Project` |
| Create / update / suspend account (3, 4, 6) | `create_`, `update_`, `suspend_user_account` | matching controllers | `UserAccount` |
| View / search accounts (5, 7) | `view_user_account`, `search_user_account` | matching controllers | `UserAccount` |
| Profile create (8) | called by `create_user_account` | `CreateUserProfileController` | `UserProfile` |
| Profile view / update / search / suspend (9-12) | `view_`, `update_`, `search_`, `suspend_user_profile` | matching controllers | `UserProfile` |
| Company create / view / search / update / delete (15-19) | `create_`, `view_`, `search_`, `update_`, `delete_company` | matching controllers | `Company` |
| Project create / view / search / update / delete, current and past (20-29) | `create_`, `view_`, `search_`, `update_`, `delete_project` | matching controllers | `Project`, `Company` |
| Public search and project details (32, 33) | `search_project`, `view_project_detail` | `SearchProjectController`, `ViewProjectDetailController` | `Project` |
| Shortlist save / view / search / compare (34-36) | `save_favourite`, `view_favourites`, `search_favourite`, `compare_favourites` | matching controllers | `Favourite` |
| Analytics (37, 38) | `view_project_analytics` | `ViewProjectAnalyticsController` | `Project` |
| Category create / view / search / update / delete (39-43) | `create_`, `view_`, `search_`, `update_`, `delete_category` | matching controllers | `Category` |
| Reports (44-46) | `generate_report` | `GenerateReportController` | `Report` |
| JSON API | `api_boundary` | search / detail / dashboard controllers | - |

Security basics: hashed passwords, parameterised SQL, role checks in the boundary, ownership checks in the controllers, session clearing, and active/suspended account handling.

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
