from datetime import date

from flask import Blueprint, flash, render_template, request

from app.controller.generate_report_controller import GenerateReportController
from app.services.auth import roles_required

bp = Blueprint("generate_report", __name__)


class GenerateReportBoundary:
    def __init__(self):
        self.controller = GenerateReportController()

    def display_page(self, result=None):
        return render_template("reports.html", result=result, today=date.today().isoformat())

    def submit_form(self, period: str, selected: str):
        success, result = self.controller.generate_report(period, selected)
        if success:
            return self.show_report(result)
        return self.show_error(result)

    def show_report(self, report: dict):
        return self.display_page(report)

    def show_error(self, message: str):
        flash(message, "danger")
        return self.display_page()


@bp.route("/reports", methods=["GET", "POST"])
@roles_required("PLATFORM_MANAGER")
def reports():
    boundary = GenerateReportBoundary()
    if request.method == "POST":
        return boundary.submit_form(request.form.get("period", "daily"),
                                    request.form.get("selected", date.today().isoformat()))
    return boundary.display_page()
