from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from app.services.database import db


class Report:
    @staticmethod
    def view_platform_counts() -> dict[str, int]:
        return {
            "users": db.one("SELECT COUNT(*) n FROM users")["n"],
            "companies": db.one("SELECT COUNT(*) n FROM companies")["n"],
            "projects": db.one("SELECT COUNT(*) n FROM projects")["n"],
            "categories": db.one("SELECT COUNT(*) n FROM categories")["n"],
            "favourites": db.one("SELECT COUNT(*) n FROM favourites")["n"],
        }

    @staticmethod
    def generate_report(period: str, selected: str) -> dict[str, Any]:
        """Daily / weekly / monthly summary. Raises ValueError for bad input."""
        if period == "daily":
            start = datetime.fromisoformat(selected).date()
            end = start + timedelta(days=1)
            label = start.isoformat()
        elif period == "weekly":
            start = date.fromisoformat(selected)
            start = start - timedelta(days=start.weekday())
            end = start + timedelta(days=7)
            label = f"{start.isoformat()} to {(end - timedelta(days=1)).isoformat()}"
        elif period == "monthly":
            year, month = int(selected[:4]), int(selected[5:7])
            start = date(year, month, 1)
            end = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
            label = start.strftime("%B %Y")
        else:
            raise ValueError("Unsupported report period.")
        lo, hi = start.isoformat(), end.isoformat()

        def count(sql: str) -> int:
            return db.one(sql, (lo, hi))["n"]

        return {
            "period": period, "label": label,
            "new_users": count("SELECT COUNT(*) n FROM users WHERE substr(created_at,1,10)>=? AND substr(created_at,1,10)<?"),
            "new_projects": count("SELECT COUNT(*) n FROM projects WHERE substr(created_at,1,10)>=? AND substr(created_at,1,10)<?"),
            "activity_events": count("SELECT COUNT(*) n FROM activity_events WHERE substr(occurred_at,1,10)>=? AND substr(occurred_at,1,10)<?"),
            "project_views": count("SELECT COUNT(*) n FROM activity_events WHERE event_type='PROJECT_VIEWED' AND substr(occurred_at,1,10)>=? AND substr(occurred_at,1,10)<?"),
            "shortlists": count("SELECT COUNT(*) n FROM favourites WHERE substr(saved_at,1,10)>=? AND substr(saved_at,1,10)<?"),
        }
