from flask import Blueprint, flash, redirect, session, url_for

from app.controller.suspend_user_profile_controller import SuspendUserProfileController
from app.services.auth import current_user_id, login_required

bp = Blueprint("suspend_user_profile", __name__)


class SuspendUserProfileBoundary:
    def __init__(self):
        self.controller = SuspendUserProfileController()

    def submit_request(self):
        success, result = self.controller.suspend_user_profile(current_user_id())
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, message: str):
        session.clear()
        flash(message, "info")
        return redirect(url_for("login_user_account.login"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_user_profile.profile"))


@bp.post("/profile/suspend")
@login_required
def profile_suspend():
    return SuspendUserProfileBoundary().submit_request()
