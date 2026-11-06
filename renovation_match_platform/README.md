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

## Features mapped to the 48 user stories

| Story | Implemented capability |
|---|---|
| 1, 13, 30, 47 | Shared secure login with active-account check |
| 2, 14, 31, 48 | Logout and session clearing |
| 3 | Admin creates an account with validation and password hashing |
| 4 | Admin updates user details, role and status |
| 5 | Admin views accounts in the account list / edit page |
| 6 | Admin suspends an account; self-suspension is blocked in admin UI |
| 7 | Admin searches accounts by username, email or name |
| 8 | Registration-style profile is created automatically when admin creates a user; seeded demo profiles are also created |
| 9 | Signed-in user updates profile details |
| 10 | Signed-in user views profile details |
| 11 | User can suspend their own account and is signed out |
| 12 | Authorized staff search profiles |
| 15 | Designer creates company information |
| 16 | Company information is displayed in the company list |
| 17 | Company search |
| 18 | Company update |
| 19 | Company deletion with project-reference protection |
| 20 | Create an IDP/project |
| 21 | View current projects (filter by status) |
| 22 | Update current projects |
| 23 | Delete current projects |
| 24 | Search current projects |
| 25 | Create a past project by selecting `PAST` status |
| 26 | View past projects |
| 27 | Update past projects |
| 28 | Delete past projects |
| 29 | Search past projects |
| 30–31 | Customer login/logout (shared auth) |
| 32 | Public project search |
| 33 | View project details; each visit increments view count |
| 34 | Save/remove a project from customer shortlist |
| 35 | Search shortlist |
| 36 | Side-by-side shortlist comparison |
| 37 | Designer analytics show per-project view counts |
| 38 | Designer analytics show shortlist counts |
| 39 | Platform manager creates category |
| 40 | View categories |
| 41 | Update category |
| 42 | Delete category; project category becomes unassigned |
| 43 | Search category |
| 44 | Daily report for selected date |
| 45 | Weekly report for selected date's week |
| 46 | Monthly report for selected month |
| 47–48 | Platform manager uses shared login/logout |

**Important requirement interpretation:** The specification's 48 stories include duplicate login/logout stories for different roles. These share one authentication implementation, with role-based authorization on protected routes. Story #8 is implemented as profile creation alongside account creation; public self-registration is not provided because the listed user stories place account creation under User Admin.

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

The tests cover health check, login/logout, role restrictions, account and category CRUD, project search and details, shortlist behavior, reports, and the BCE layering rules. In the project report, include screenshots of a failing test before implementation and a passing test after implementation; the test suite alone is not sufficient evidence that TDD was followed historically.

## CI/CD

A GitHub Actions workflow is provided in `.github/workflows/ci.yml`. It installs the backend dependencies and runs automated tests on each push and pull request. This demonstrates continuous integration. It does **not** deploy the app to a live host; if your group claims continuous delivery, add a deployment job to your chosen host and include real screenshots/logs of a successful deployment.

## Before submission

1. Confirm the team accepts Python/Flask as the implementation stack; the project specification requires an object-oriented backend but does not mandate a language.
2. Run all tests and fix any failures on the machine used for the demo.
3. Use Taiga to map each story to tasks, assign owners, and capture weekly evidence. Do not fabricate sprint evidence.
4. Capture real screenshots for the report: each role, CRUD operations, reports, seed data, tests, and GitHub Actions run.
5. Change the development secret and demo passwords before exposing the app to a network.
6. Add CSRF protection, rate limiting, password reset, production secret management, and HTTPS before production use. This is a coursework demonstration, not a production-ready public service.
