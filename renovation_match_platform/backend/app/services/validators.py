from __future__ import annotations

from typing import Any

from app.config import PROJECT_STATUSES


def validate_project(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalise project form data. Raises ValueError on bad input."""
    if any(not str(data.get(k, "")).strip() for k in ("company_id", "title")):
        raise ValueError("Company and project title are required.")
    try:
        company_id = int(data["company_id"])
        budget = float(data.get("budget") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Company and budget must be valid numbers.") from exc
    if budget < 0:
        raise ValueError("Budget cannot be negative.")
    status = data.get("status", "CURRENT")
    if status not in PROJECT_STATUSES:
        raise ValueError("Status must be CURRENT or PAST.")
    return {
        "company_id": company_id,
        "category_id": data.get("category_id") or None,
        "title": data["title"].strip(),
        "description": data.get("description", "").strip(),
        "location": data.get("location", "").strip(),
        "budget": budget,
        "status": status,
        "image_url": data.get("image_url", "").strip(),
    }
