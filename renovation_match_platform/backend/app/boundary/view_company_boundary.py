from flask import Blueprint, flash, render_template

from app.controller.view_company_controller import ViewCompanyController
from app.services.auth import current_user, roles_required

bp = Blueprint("view_company", __name__)


class ViewCompanyBoundary:
    def __init__(self):
        self.controller = ViewCompanyController()

    def display_page(self):
        success, result = self.controller.view_all_companies(current_user())
        if success:
            return self.show_companies(result)
        return self.show_error(result)

    def show_companies(self, rows):
        return render_template("companies.html", rows=rows, q="")

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("companies.html", rows=[], q="")


@bp.get("/companies")
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def companies():
    return ViewCompanyBoundary().display_page()
