from __future__ import annotations

from datetime import datetime

from app.services.database import db

_FAV_JOIN = """SELECT p.*,c.name company_name,cat.name category_name,f.saved_at
               FROM favourites f JOIN projects p ON p.id=f.project_id
               JOIN companies c ON c.id=p.company_id
               LEFT JOIN categories cat ON cat.id=p.category_id"""


class Favourite:
    def __init__(self, customer_id: int, project_id: int):
        self.customer_id = customer_id
        self.project_id = project_id

    def save_favourite(self) -> None:
        db.execute("INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)",
                   (self.customer_id, self.project_id, datetime.now().isoformat(timespec="seconds")))

    def remove_favourite(self) -> None:
        db.execute("DELETE FROM favourites WHERE customer_id=? AND project_id=?",
                   (self.customer_id, self.project_id))

    @staticmethod
    def is_saved(customer_id: int, project_id: int) -> bool:
        return db.one("SELECT 1 FROM favourites WHERE customer_id=? AND project_id=?",
                      (customer_id, project_id)) is not None

    @staticmethod
    def view_favourites(customer_id: int):
        return db.all(_FAV_JOIN + " WHERE f.customer_id=? ORDER BY f.saved_at DESC", (customer_id,))

    @staticmethod
    def search_favourites(customer_id: int, keyword: str):
        like = f"%{keyword}%"
        return db.all(_FAV_JOIN + """ WHERE f.customer_id=? AND (p.title LIKE ? OR c.name LIKE ? OR p.location LIKE ?)
                                     ORDER BY f.saved_at DESC""", (customer_id, like, like, like))

    @staticmethod
    def compare_favourites(customer_id: int):
        return db.all(_FAV_JOIN + " WHERE f.customer_id=? ORDER BY p.budget", (customer_id,))
