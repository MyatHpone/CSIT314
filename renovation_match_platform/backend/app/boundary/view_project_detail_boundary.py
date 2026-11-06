from flask import Blueprint, render_template

from app.controller.view_project_detail_controller import ViewProjectDetailController
from app.services.auth import abort_on_access_error, current_user

bp = Blueprint("view_project_detail", __name__)


class ViewProjectDetailBoundary:
    def __init__(self):
        self.controller = ViewProjectDetailController()

    def display_page(self, project_id: int):
        success, result = self.controller.view_project(project_id, current_user())
        if success:
            return self.show_project(result)
        return self.show_error(result)

    def show_project(self, data: dict):
        return render_template("project_detail.html", row=data["project"], saved=data["saved"])

    def show_error(self, message: str):
        abort_on_access_error(message)


@bp.get("/projects/<int:project_id>")
def project_detail(project_id: int):
    return ViewProjectDetailBoundary().display_page(project_id)
