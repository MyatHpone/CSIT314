from flask import Blueprint, flash, redirect, request, url_for

from app.controller.save_favourite_controller import SaveFavouriteController
from app.services.auth import abort_on_access_error, current_user_id, roles_required

bp = Blueprint("save_favourite", __name__)


class SaveFavouriteBoundary:
    def __init__(self):
        self.controller = SaveFavouriteController()

    def submit_request(self, project_id: int):
        success, result = self.controller.save_favourite(current_user_id(), project_id)
        if success:
            return self.show_success(result)
        abort_on_access_error(result)
        return self.show_error(result)

    def show_success(self, message: str):
        flash(message, "success")
        return redirect(request.referrer or url_for("view_project.projects"))

    def show_error(self, message: str):
        flash(message, "danger")
        return redirect(request.referrer or url_for("view_project.projects"))


@bp.post("/projects/<int:project_id>/favourite")
@roles_required("CUSTOMER")
def favourite(project_id: int):
    return SaveFavouriteBoundary().submit_request(project_id)
