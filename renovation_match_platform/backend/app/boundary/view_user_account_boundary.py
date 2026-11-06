from flask import Blueprint, flash, render_template

from app.controller.view_user_account_controller import ViewUserAccountController
from app.services.auth import roles_required

bp = Blueprint("view_user_account", __name__)


class ViewUserAccountBoundary:
    def __init__(self):
        self.controller = ViewUserAccountController()

    def display_page(self):
        success, result = self.controller.view_all_user_accounts()
        if success:
            return self.show_accounts(result)
        return self.show_error(result)

    def show_accounts(self, rows):
        return render_template("users.html", rows=rows, q="")

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("users.html", rows=[], q="")


@bp.get("/users")
@roles_required("USER_ADMIN")
def users_list():
    return ViewUserAccountBoundary().display_page()
