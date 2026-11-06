from flask import Blueprint, flash, render_template, request

from app.controller.search_project_controller import SearchProjectController

bp = Blueprint("search_project", __name__)


class SearchProjectBoundary:
    def __init__(self):
        self.controller = SearchProjectController()

    def submit_search(self, keyword: str, status: str):
        success, result = self.controller.search_projects(keyword, status)
        if success:
            return self.show_results(result, keyword, status)
        return self.show_error(result, keyword, status)

    def show_results(self, rows, keyword: str, status: str):
        return render_template("projects.html", rows=rows, q=keyword, status=status)

    def show_error(self, message: str, keyword: str, status: str):
        flash(message, "danger")
        return render_template("projects.html", rows=[], q=keyword, status=status)


@bp.get("/projects/search")
def project_search():
    return SearchProjectBoundary().submit_search(request.args.get("q", "").strip(),
                                                 request.args.get("status", ""))
