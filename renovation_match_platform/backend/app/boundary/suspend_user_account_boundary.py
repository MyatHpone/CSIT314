from flask import Blueprint, flash, redirect, url_for

from app.controller.suspend_user_account_controller import SuspendUserAccountController
from app.services.auth import abort_on_access_error, current_user_id, roles_required

bp = Blueprint("suspend_user_account", __name__)


class SuspendUserAccountBoundary:
    def __init__(self):
        self.controller = SuspendUserAccountController()

    def submit_request(self, user_id: int):
        success, result = self.controller.suspend_user_account(current_user_id(), user_id)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_user_account.users_list"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_user_account.users_list"))


@bp.post("/users/<int:user_id>/suspend")
@roles_required("USER_ADMIN")
def user_suspend(user_id: int):
    return SuspendUserAccountBoundary().submit_request(user_id)
