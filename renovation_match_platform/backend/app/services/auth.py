"""Session / authorisation helpers used by the Boundary layer."""
from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort, flash, g, jsonify, redirect, request, session, url_for

from app.entity.user_account import UserAccount
from app.services.results import FORBIDDEN, NOT_FOUND


def load_current_user() -> None:
    uid = session.get("user_id")
    g.current_user = UserAccount.view_user_account(uid) if uid else None
    if g.current_user and g.current_user["status"] != "ACTIVE":
        session.clear()
        g.current_user = None


def current_user() -> dict | None:
    return g.get("current_user")


def current_user_id() -> int | None:
    user = current_user()
    return int(user["id"]) if user else None


def login_required(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            if request.path.startswith("/api/"):
                return jsonify(error="Login required"), 401
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login_user_account.login"))
        return fn(*args, **kwargs)
    return wrapper


def roles_required(*roles: str):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                if request.path.startswith("/api/"):
                    return jsonify(error="Login required"), 401
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login_user_account.login"))
            if user["role"] not in roles:
                if request.path.startswith("/api/"):
                    return jsonify(error="You do not have permission for this action."), 403
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def abort_on_access_error(message: str) -> None:
    """Translate controller NOT_FOUND / FORBIDDEN results into HTTP errors."""
    if message == NOT_FOUND:
        abort(404)
    if message == FORBIDDEN:
        abort(403)
