from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.controller.update_user_account_controller import UpdateUserAccountController
from app.controller.view_user_account_controller import ViewUserAccountController
from app.services.auth import abort_on_access_error, current_user_id, roles_required

bp = Blueprint("update_user_account", __name__)


class UpdateUserAccountBoundary:
    def __init__(self):
        self.controller = UpdateUserAccountController()
        self.row = None

    def display_page(self, user_id: int):
        found, row = ViewUserAccountController().view_user_account(user_id)
        if not found:
            abort(404)
        self.row = row
        return render_template("user_form.html", row=row)

    def submit_form(self, user_id: int, form: dict):
        found, row = ViewUserAccountController().view_user_account(user_id)
        if not found:
            abort(404)
        self.row = row
        success, result = self.controller.update_user_account(current_user_id(), user_id, form)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_user_account.users_list"))

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("user_form.html", row=self.row)


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("USER_ADMIN")
def user_edit(user_id: int):
    boundary = UpdateUserAccountBoundary()
    if request.method == "POST":
        return boundary.submit_form(user_id, request.form.to_dict())
    return boundary.display_page(user_id)
