from flask import Blueprint, flash, redirect, url_for

from app.controller.delete_project_controller import DeleteProjectController
from app.services.auth import abort_on_access_error, current_user, roles_required

bp = Blueprint("delete_project", __name__)


class DeleteProjectBoundary:
    def __init__(self):
        self.controller = DeleteProjectController()

    def submit_request(self, project_id: int):
        success, result = self.controller.delete_project(current_user(), project_id)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_project.projects"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_project.projects"))


@bp.post("/projects/<int:project_id>/delete")
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def project_delete(project_id: int):
    return DeleteProjectBoundary().submit_request(project_id)
