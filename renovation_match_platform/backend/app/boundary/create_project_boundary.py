from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.create_project_controller import CreateProjectController
from app.controller.view_project_controller import ViewProjectController
from app.services.auth import current_user, roles_required

bp = Blueprint("create_project", __name__)


class CreateProjectBoundary:
    def __init__(self):
        self.controller = CreateProjectController()

    def display_page(self):
        _, (companies, categories) = ViewProjectController().view_form_options(current_user())
        return render_template("project_form.html", row=None, companies=companies, categories=categories)

    def submit_form(self, form: dict):
        success, result = self.controller.create_project(current_user(), form)
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_project.projects"))

    def show_error(self, message: str):
        flash(message, "danger")
        return self.display_page()


@bp.route("/projects/new", methods=["GET", "POST"])
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def project_new():
    boundary = CreateProjectBoundary()
    if request.method == "POST":
        return boundary.submit_form(request.form.to_dict())
    return boundary.display_page()
