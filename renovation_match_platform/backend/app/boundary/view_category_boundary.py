from flask import Blueprint, flash, render_template

from app.controller.view_category_controller import ViewCategoryController
from app.services.auth import roles_required

bp = Blueprint("view_category", __name__)


class ViewCategoryBoundary:
    def __init__(self):
        self.controller = ViewCategoryController()

    def display_page(self):
        success, result = self.controller.view_all_categories()
        if success:
            return self.show_categories(result)
        return self.show_error(result)

    def show_categories(self, rows):
        return render_template("categories.html", rows=rows, q="")

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("categories.html", rows=[], q="")


@bp.get("/categories")
@roles_required("PLATFORM_MANAGER", "USER_ADMIN")
def categories():
    return ViewCategoryBoundary().display_page()
