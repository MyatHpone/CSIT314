from app.entity.category import Category


class SearchCategoryController:
    def search_categories(self, keyword: str):
        try:
            return True, Category.search_categories(keyword)
        except Exception as e:
            return False, str(e)
