from flask import Blueprint, flash, render_template

from app.controller.view_favourites_controller import ViewFavouritesController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("view_favourites", __name__)


class ViewFavouritesBoundary:
    def __init__(self):
        self.controller = ViewFavouritesController()

    def display_page(self):
        success, result = self.controller.view_favourites(current_user_id())
        if success:
            return self.show_favourites(result)
        return self.show_error(result)

    def show_favourites(self, rows):
        return render_template("shortlist.html", rows=rows, q="")

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("shortlist.html", rows=[], q="")


@bp.get("/shortlist")
@roles_required("CUSTOMER")
def shortlist():
    return ViewFavouritesBoundary().display_page()
