from flask import Blueprint, abort, render_template

from app.controller.view_user_profile_controller import ViewUserProfileController
from app.services.auth import current_user_id, login_required

bp = Blueprint("view_user_profile", __name__)


class ViewUserProfileBoundary:
    def __init__(self):
        self.controller = ViewUserProfileController()

    def display_page(self):
        success, result = self.controller.view_user_profile(current_user_id())
        if success:
            return self.show_profile(result)
        return self.show_error(result)

    def show_profile(self, profile):
        return render_template("profile.html", row=profile)

    def show_error(self, message: str):
        abort(404)


@bp.get("/profile")
@login_required
def profile():
    return ViewUserProfileBoundary().display_page()
