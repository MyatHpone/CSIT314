from flask import Blueprint, flash, redirect, request, url_for

from app.controller.update_user_profile_controller import UpdateUserProfileController
from app.services.auth import current_user_id, login_required

bp = Blueprint("update_user_profile", __name__)


class UpdateUserProfileBoundary:
    def __init__(self):
        self.controller = UpdateUserProfileController()

    def submit_form(self, form: dict):
        success, result = self.controller.update_user_profile(current_user_id(), form)
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_user_profile.profile"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_user_profile.profile"))


@bp.post("/profile")
@login_required
def profile_update():
    return UpdateUserProfileBoundary().submit_form(request.form.to_dict())
