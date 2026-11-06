from flask import Blueprint, flash, render_template, request

from app.controller.search_favourite_controller import SearchFavouriteController
from app.services.auth import current_user_id, roles_required

bp = Blueprint("search_favourite", __name__)


class SearchFavouriteBoundary:
    def __init__(self):
        self.controller = SearchFavouriteController()

    def submit_search(self, keyword: str):
        success, result = self.controller.search_favourites(current_user_id(), keyword)
        if success:
            return self.show_results(result, keyword)
        return self.show_error(result, keyword)

    def show_results(self, rows, keyword: str):
        return render_template("shortlist.html", rows=rows, q=keyword)

    def show_error(self, message: str, keyword: str):
        flash(message, "danger")
        return render_template("shortlist.html", rows=[], q=keyword)


@bp.get("/shortlist/search")
@roles_required("CUSTOMER")
def shortlist_search():
    return SearchFavouriteBoundary().submit_search(request.args.get("q", "").strip())
