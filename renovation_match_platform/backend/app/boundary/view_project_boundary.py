from flask import Blueprint, flash, render_template, request

from app.controller.view_project_controller import ViewProjectController

bp = Blueprint("view_project", __name__)


class ViewProjectBoundary:
    def __init__(self):
        self.controller = ViewProjectController()

    def display_page(self, status: str = ""):
        success, result = self.controller.view_projects(status)
        if success:
            return self.show_projects(result, status)
        return self.show_error(result, status)

    def show_projects(self, rows, status: str):
        return render_template("projects.html", rows=rows, q="", status=status)

    def show_error(self, message: str, status: str):
        flash(message, "danger")
        return render_template("projects.html", rows=[], q="", status=status)


@bp.get("/projects")
def projects():
    return ViewProjectBoundary().display_page(request.args.get("status", ""))
