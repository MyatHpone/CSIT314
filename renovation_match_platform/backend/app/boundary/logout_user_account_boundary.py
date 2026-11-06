from flask import Blueprint, flash, redirect, session, url_for

from app.controller.logout_user_account_controller import LogoutUserAccountController
from app.services.auth import current_user_id, login_required

bp = Blueprint("logout_user_account", __name__)


class LogoutUserAccountBoundary:
    def __init__(self):
        self.controller = LogoutUserAccountController()

    def submit_request(self):
        success, result = self.controller.logout_user(current_user_id())
        session.clear()
        return self.show_success(result if success else "You have logged out.")

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("login_user_account.login"))


@bp.post("/logout")
@login_required
def logout():
    return LogoutUserAccountBoundary().submit_request()
