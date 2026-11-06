from flask import Blueprint, flash, render_template, request

from app.controller.search_user_profile_controller import SearchUserProfileController
from app.services.auth import roles_required

bp = Blueprint("search_user_profile", __name__)


class SearchUserProfileBoundary:
    def __init__(self):
        self.controller = SearchUserProfileController()

    def submit_search(self, keyword: str):
        success, result = self.controller.search_user_profiles(keyword)
        if success:
            return self.show_results(result, keyword)
        return self.show_error(result, keyword)

    def show_results(self, rows, keyword: str):
        return render_template("profiles.html", rows=rows, q=keyword)

    def show_error(self, message: str, keyword: str):
        flash(message, "danger")
        return render_template("profiles.html", rows=[], q=keyword)


@bp.get("/profiles")
@roles_required("USER_ADMIN", "PLATFORM_MANAGER", "INTERIOR_DESIGNER")
def profiles_search():
    return SearchUserProfileBoundary().submit_search(request.args.get("q", "").strip())
