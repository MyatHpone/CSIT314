from flask import Blueprint, redirect, render_template, url_for

from app.controller.view_dashboard_controller import ViewDashboardController
from app.services.auth import current_user, login_required

bp = Blueprint("view_dashboard", __name__)


class ViewDashboardBoundary:
    def __init__(self):
        self.controller = ViewDashboardController()

    def display_page(self):
        success, result = self.controller.view_dashboard()
        if success:
            return self.show_dashboard(result)
        return self.show_error(result)

    def show_dashboard(self, data: dict):
        return render_template("dashboard.html", counts=data["counts"], projects=data["projects"])

    def show_error(self, message: str):
        return render_template("error.html", code=500, message=message), 500


@bp.get("/")
def index():
    target = "view_dashboard.dashboard" if current_user() else "login_user_account.login"
    return redirect(url_for(target))


@bp.get("/dashboard")
@login_required
def dashboard():
    return ViewDashboardBoundary().display_page()
