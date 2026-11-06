from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.update_project_controller import UpdateProjectController
from app.controller.view_project_controller import ViewProjectController
from app.services.auth import abort_on_access_error, current_user, roles_required

bp = Blueprint("update_project", __name__)


class UpdateProjectBoundary:
    def __init__(self):
        self.controller = UpdateProjectController()
        self.row = None

    def display_page(self, project_id: int):
        found, row = self.controller.view_project_for_edit(current_user(), project_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        return self._render_form()

    def submit_form(self, project_id: int, form: dict):
        found, row = self.controller.view_project_for_edit(current_user(), project_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        success, result = self.controller.update_project(current_user(), project_id, form)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_project.projects"))

    def show_error(self, message: str):
        flash(message, "danger")
        return self._render_form()

    def _render_form(self):
        _, (companies, categories) = ViewProjectController().view_form_options(current_user(), all_companies=True)
        return render_template("project_form.html", row=self.row, companies=companies, categories=categories)


@bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def project_edit(project_id: int):
    boundary = UpdateProjectBoundary()
    if request.method == "POST":
        return boundary.submit_form(project_id, request.form.to_dict())
    return boundary.display_page(project_id)
