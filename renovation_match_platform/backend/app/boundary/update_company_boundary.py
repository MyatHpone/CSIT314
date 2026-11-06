from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.update_company_controller import UpdateCompanyController
from app.controller.view_company_controller import ViewCompanyController
from app.services.auth import abort_on_access_error, current_user, roles_required

bp = Blueprint("update_company", __name__)


class UpdateCompanyBoundary:
    def __init__(self):
        self.controller = UpdateCompanyController()
        self.row = None

    def display_page(self, company_id: int):
        found, row = ViewCompanyController().view_company(current_user(), company_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        return render_template("company_form.html", row=row)

    def submit_form(self, company_id: int, form: dict):
        found, row = ViewCompanyController().view_company(current_user(), company_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        success, result = self.controller.update_company(current_user(), company_id, form)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_company.companies"))

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("company_form.html", row=self.row)


@bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def company_edit(company_id: int):
    boundary = UpdateCompanyBoundary()
    if request.method == "POST":
        return boundary.submit_form(company_id, request.form.to_dict())
    return boundary.display_page(company_id)
