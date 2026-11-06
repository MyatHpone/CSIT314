from flask import Blueprint, flash, render_template, request

from app.controller.search_user_account_controller import SearchUserAccountController
from app.services.auth import roles_required

bp = Blueprint("search_user_account", __name__)


class SearchUserAccountBoundary:
    def __init__(self):
        self.controller = SearchUserAccountController()

    def submit_search(self, keyword: str):
        success, result = self.controller.search_user_accounts(keyword)
        if success:
            return self.show_results(result, keyword)
        return self.show_error(result, keyword)

    def show_results(self, rows, keyword: str):
        return render_template("users.html", rows=rows, q=keyword)

    def show_error(self, message: str, keyword: str):
        flash(message, "danger")
        return render_template("users.html", rows=[], q=keyword)


@bp.get("/users/search")
@roles_required("USER_ADMIN")
def users_search():
    return SearchUserAccountBoundary().submit_search(request.args.get("q", "").strip())
