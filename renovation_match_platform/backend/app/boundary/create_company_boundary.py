from flask import Blueprint, flash, redirect, request, url_for

from app.controller.create_company_controller import CreateCompanyController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("create_company", __name__)


class CreateCompanyBoundary:
    def __init__(self):
        self.controller = CreateCompanyController()

    def submit_form(self, form: dict):
        success, result = self.controller.create_company(current_user_id(), form)
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_company.companies"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_company.companies"))


@bp.post("/companies")
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def company_create():
    return CreateCompanyBoundary().submit_form(request.form.to_dict())
