from __future__ import annotations

from datetime import datetime

from app.services.database import db


class Category:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def create_category(self) -> int:
        return db.execute("INSERT INTO categories(name,description,created_at) VALUES(?,?,?)",
                          (self.name, self.description, datetime.now().isoformat(timespec="seconds")))

    @staticmethod
    def view_all_categories():
        return db.all("SELECT * FROM categories ORDER BY name")

    @staticmethod
    def search_categories(keyword: str):
        like = f"%{keyword}%"
        return db.all("SELECT * FROM categories WHERE name LIKE ? OR description LIKE ? ORDER BY name",
                      (like, like))

    @staticmethod
    def view_category(category_id: int):
        return db.one("SELECT * FROM categories WHERE id=?", (category_id,))

    @staticmethod
    def update_category(category_id: int, name: str, description: str) -> None:
        db.execute("UPDATE categories SET name=?,description=? WHERE id=?", (name, description, category_id))

    @staticmethod
    def delete_category(category_id: int) -> None:
        db.execute("DELETE FROM categories WHERE id=?", (category_id,))
