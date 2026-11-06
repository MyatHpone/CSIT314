from flask import Blueprint, flash, redirect, url_for

from app.controller.delete_category_controller import DeleteCategoryController
from app.services.auth import abort_on_access_error, current_user_id, roles_required

bp = Blueprint("delete_category", __name__)


class DeleteCategoryBoundary:
    def __init__(self):
        self.controller = DeleteCategoryController()

    def submit_request(self, category_id: int):
        success, result = self.controller.delete_category(current_user_id(), category_id)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(url_for("view_category.categories"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(url_for("view_category.categories"))


@bp.post("/categories/<int:category_id>/delete")
@roles_required("PLATFORM_MANAGER")
def category_delete(category_id: int):
    return DeleteCategoryBoundary().submit_request(category_id)
