from flask import Blueprint, flash, render_template, request

from app.controller.search_category_controller import SearchCategoryController
from app.services.auth import roles_required

bp = Blueprint("search_category", __name__)


class SearchCategoryBoundary:
    def __init__(self):
        self.controller = SearchCategoryController()

    def submit_search(self, keyword: str):
        success, result = self.controller.search_categories(keyword)
        if success:
            return self.show_results(result, keyword)
        return self.show_error(result, keyword)

    def show_results(self, rows, keyword: str):
        return render_template("categories.html", rows=rows, q=keyword)

    def show_error(self, message: str, keyword: str):
        flash(message, "danger")
        return render_template("categories.html", rows=[], q=keyword)


@bp.get("/categories/search")
@roles_required("PLATFORM_MANAGER", "USER_ADMIN")
def category_search():
    return SearchCategoryBoundary().submit_search(request.args.get("q", "").strip())
