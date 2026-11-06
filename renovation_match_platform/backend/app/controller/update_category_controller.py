import sqlite3

from app.entity.activity_event import ActivityEvent
from app.entity.category import Category
from app.services.results import NOT_FOUND


class UpdateCategoryController:
    def update_category(self, actor_id: int, category_id: int, data: dict):
        try:
            if not Category.view_category(category_id):
                return False, NOT_FOUND
            name = data.get("name", "").strip()
            if not name:
                return False, "Category name is required."
            try:
                Category.update_category(category_id, name, data.get("description", "").strip())
            except sqlite3.IntegrityError:
                return False, "A category with that name already exists."
            ActivityEvent.log(actor_id, "CATEGORY_UPDATED", "category", category_id)
            return True, "Category updated."
        except Exception as e:
            return False, str(e)
