from app.entity.category import Category
from app.services.results import NOT_FOUND


class ViewCategoryController:
    def view_all_categories(self):
        try:
            return True, Category.view_all_categories()
        except Exception as e:
            return False, str(e)

    def view_category(self, category_id: int):
        try:
            category = Category.view_category(category_id)
            if not category:
                return False, NOT_FOUND
            return True, category
        except Exception as e:
            return False, str(e)
