from flask import Blueprint, flash, render_template

from app.controller.compare_favourites_controller import CompareFavouritesController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("compare_favourites", __name__)


class CompareFavouritesBoundary:
    def __init__(self):
        self.controller = CompareFavouritesController()

    def display_page(self):
        success, result = self.controller.compare_favourites(current_user_id())
        if success:
            return self.show_comparison(result)
        return self.show_error(result)

    def show_comparison(self, rows):
        return render_template("compare.html", rows=rows)

    def show_error(self, message: str):
        flash(message, "danger")
        return render_template("compare.html", rows=[])


@bp.get("/compare")
@roles_required("CUSTOMER")
def compare():
    return CompareFavouritesBoundary().display_page()
