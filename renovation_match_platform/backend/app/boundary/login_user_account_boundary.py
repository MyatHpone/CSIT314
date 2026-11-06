from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.controller.login_user_account_controller import LoginUserAccountController

bp = Blueprint("login_user_account", __name__)


class LoginUserAccountBoundary:
    def __init__(self):
        self.controller = LoginUserAccountController()

    def display_page(self):
        return render_template("login.html")

    def submit_form(self, username: str, password: str):
        success, result = self.controller.login_user(username, password)
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, account):
        session.clear()
        session["user_id"] = account["id"]
        return redirect(url_for("view_dashboard.dashboard"))

    def show_error(self, message: str):
        flash(message, "danger")
        return self.display_page()


@bp.route("/login", methods=["GET", "POST"])
def login():
    boundary = LoginUserAccountBoundary()
    if request.method == "POST":
        return boundary.submit_form(request.form.get("username", ""), request.form.get("password", ""))
    return boundary.display_page()
