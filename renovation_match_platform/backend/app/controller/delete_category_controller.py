from app.entity.activity_event import ActivityEvent
from app.entity.category import Category
from app.services.results import NOT_FOUND


class DeleteCategoryController:
    def delete_category(self, actor_id: int, category_id: int):
        try:
            if not Category.view_category(category_id):
                return False, NOT_FOUND
            Category.delete_category(category_id)
            ActivityEvent.log(actor_id, "CATEGORY_DELETED", "category", category_id)
            return True, "Category deleted. Projects retain their records with no category."
        except Exception as e:
            return False, str(e)
