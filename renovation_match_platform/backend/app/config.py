import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

DATABASE = os.environ.get("RENOVATION_DB", str(BACKEND_DIR / "renovation_match.db"))
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-secret")

ROLES = ("USER_ADMIN", "INTERIOR_DESIGNER", "CUSTOMER", "PLATFORM_MANAGER")
ACCOUNT_STATUSES = ("ACTIVE", "SUSPENDED")
PROJECT_STATUSES = ("CURRENT", "PAST")
