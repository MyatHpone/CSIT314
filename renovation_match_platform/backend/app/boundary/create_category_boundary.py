from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.create_category_controller import CreateCategoryController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("create_category", __name__)


class CreateCategoryBoundary:
    def __init__(self):
        self.controller = CreateCategoryController()

    def display_page(self):
        return render_template("category_form.html", row=None)

    def submit_form(self, form: dict):
        success, result = self.controller.create_category(current_user_id(), form)
        if success:
            return self.show_success(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_category.categories"))

    def show_error(self, message: str):
        flash(message, "danger")
        return self.display_page()


@bp.route("/categories/new", methods=["GET", "POST"])
@roles_required("PLATFORM_MANAGER")
def category_new():
    boundary = CreateCategoryBoundary()
    if request.method == "POST":
        return boundary.submit_form(request.form.to_dict())
    return boundary.display_page()
