from app.entity.favourite import Favourite


class CompareFavouritesController:
    """Story 36: side-by-side comparison of shortlisted projects."""

    def compare_favourites(self, customer_id: int):
        try:
            return True, Favourite.compare_favourites(customer_id)
        except Exception as e:
            return False, str(e)
