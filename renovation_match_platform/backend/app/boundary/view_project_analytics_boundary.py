from flask import Blueprint, flash, render_template

from app.controller.view_project_analytics_controller import ViewProjectAnalyticsController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("view_project_analytics", __name__)


class ViewProjectAnalyticsBoundary:
    def __init__(self):
        self.controller = ViewProjectAnalyticsController()

    def display_page(self):
        success, result = self.controller.view_project_analytics(current_user_id())
        if success:
            return self.show_analytics(result)
        return self.show_error(result)

    def show_analytics(self, rows):
        return render_template("analytics.html", rows=rows)

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("analytics.html", rows=[])


@bp.get("/analytics")
@roles_required("INTERIOR_DESIGNER")
def analytics():
    return ViewProjectAnalyticsBoundary().display_page()
