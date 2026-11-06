import sqlite3

from app.entity.activity_event import ActivityEvent
from app.entity.category import Category


class CreateCategoryController:
    def create_category(self, actor_id: int, data: dict):
        try:
            name = data.get("name", "").strip()
            if not name:
                return False, "Category name is required."
            try:
                category_id = Category(name, data.get("description", "").strip()).create_category()
            except sqlite3.IntegrityError:
                return False, "A category with that name already exists."
            ActivityEvent.log(actor_id, "CATEGORY_CREATED", "category", category_id)
            return True, "Category created."
        except Exception as e:
            return False, str(e)
