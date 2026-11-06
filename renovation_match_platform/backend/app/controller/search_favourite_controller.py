from app.entity.favourite import Favourite


class SearchFavouriteController:
    """Story 35: search the customer's shortlist."""

    def search_favourites(self, customer_id: int, keyword: str):
        try:
            return True, Favourite.search_favourites(customer_id, keyword)
        except Exception as e:
            return False, str(e)
