from flask import Blueprint, flash, redirect, url_for

from app.controller.delete_company_controller import DeleteCompanyController
from app.services.auth import abort_on_access_error, current_user, roles_required

bp = Blueprint("delete_company", __name__)


class DeleteCompanyBoundary:
    def __init__(self):
        self.controller = DeleteCompanyController()

    def submit_request(self, company_id: int):
        success, result = self.controller.delete_company(current_user(), company_id)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_company.companies"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_company.companies"))


@bp.post("/companies/<int:company_id>/delete")
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def company_delete(company_id: int):
    return DeleteCompanyBoundary().submit_request(company_id)
