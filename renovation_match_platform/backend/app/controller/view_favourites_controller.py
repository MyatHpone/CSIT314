from app.entity.favourite import Favourite


class ViewFavouritesController:
    def view_favourites(self, customer_id: int):
        try:
            return True, Favourite.view_favourites(customer_id)
        except Exception as e:
            return False, str(e)
