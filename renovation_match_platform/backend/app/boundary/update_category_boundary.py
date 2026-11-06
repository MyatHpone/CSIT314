from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controller.update_category_controller import UpdateCategoryController
from app.controller.view_category_controller import ViewCategoryController
from app.services.auth import abort_on_access_error, current_user_id, roles_required

bp = Blueprint("update_category", __name__)


class UpdateCategoryBoundary:
    def __init__(self):
        self.controller = UpdateCategoryController()
        self.row = None

    def display_page(self, category_id: int):
        found, row = ViewCategoryController().view_category(category_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        return render_template("category_form.html", row=row)

    def submit_form(self, category_id: int, form: dict):
        found, row = ViewCategoryController().view_category(category_id)
        if not found:
            abort_on_access_error(row)
        self.row = row
        success, result = self.controller.update_category(current_user_id(), category_id, form)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_category.categories"))

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("category_form.html", row=self.row)


@bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@roles_required("PLATFORM_MANAGER")
def category_edit(category_id: int):
    boundary = UpdateCategoryBoundary()
    if request.method == "POST":
        return boundary.submit_form(category_id, request.form.to_dict())
    return boundary.display_page(category_id)
