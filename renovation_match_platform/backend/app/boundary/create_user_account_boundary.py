from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.create_user_account_controller import CreateUserAccountController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("create_user_account", __name__)


class CreateUserAccountBoundary:
    def __init__(self):
        self.controller = CreateUserAccountController()

    def display_page(self):
        return render_template("user_form.html", row=None)

    def submit_form(self, form: dict):
        success, result = self.controller.create_user_account(current_user_id(), form)
        if success:
            return self.show_success("User account created.")
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_user_account.users_list"))

    def show_error(self, message: str):
        flash(message, "danger")
        return self.display_page()


@bp.route("/users/new", methods=["GET", "POST"])
@roles_required("USER_ADMIN")
def user_new():
    boundary = CreateUserAccountBoundary()
    if request.method == "POST":
        return boundary.submit_form(request.form.to_dict())
    return boundary.display_page()
