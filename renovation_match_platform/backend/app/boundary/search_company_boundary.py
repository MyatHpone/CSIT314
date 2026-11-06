from flask import Blueprint, flash, render_template, request

from app.controller.search_company_controller import SearchCompanyController
from app.services.auth import current_user, roles_required

bp = Blueprint("search_company", __name__)


class SearchCompanyBoundary:
    def __init__(self):
        self.controller = SearchCompanyController()

    def submit_search(self, keyword: str):
        success, result = self.controller.search_companies(current_user(), keyword)
        if success:
            return self.show_results(result, keyword)
        return self.show_error(result, keyword)

    def show_results(self, rows, keyword: str):
        return render_template("companies.html", rows=rows, q=keyword)

    def show_error(self, message: str, keyword: str):
        flash(message, "danger")
        return render_template("companies.html", rows=[], q=keyword)


@bp.get("/companies/search")
@roles_required("INTERIOR_DESIGNER", "USER_ADMIN")
def company_search():
    return SearchCompanyBoundary().submit_search(request.args.get("q", "").strip())
