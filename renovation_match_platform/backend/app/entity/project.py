from __future__ import annotations

from datetime import datetime

from app.services.database import db

_PROJECT_JOIN = """SELECT p.*, c.name AS company_name, c.description AS company_description,
                          cat.name AS category_name
                   FROM projects p JOIN companies c ON c.id=p.company_id
                   LEFT JOIN categories cat ON cat.id=p.category_id"""


class Project:
    def __init__(self, company_id: int, category_id, title: str, description: str, location: str,
                 budget: float, status: str, image_url: str):
        self.company_id = company_id
        self.category_id = category_id
        self.title = title
        self.description = description
        self.location = location
        self.budget = budget
        self.status = status
        self.image_url = image_url

    def create_project(self) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        return db.execute("""INSERT INTO projects(company_id,category_id,title,description,location,budget,status,
                                                  image_url,created_at,updated_at)
                             VALUES(?,?,?,?,?,?,?,?,?,?)""",
                          (self.company_id, self.category_id, self.title, self.description, self.location,
                           self.budget, self.status, self.image_url, now, now))

    @staticmethod
    def view_all_projects(status: str = ""):
        return Project.search_projects("", status)

    @staticmethod
    def search_projects(keyword: str = "", status: str = ""):
        sql = _PROJECT_JOIN + " WHERE 1=1"
        params: list = []
        if keyword:
            like = f"%{keyword.strip()}%"
            sql += " AND (p.title LIKE ? OR p.description LIKE ? OR p.location LIKE ? OR c.name LIKE ? OR cat.name LIKE ?)"
            params.extend([like] * 5)
        if status in ("CURRENT", "PAST"):
            sql += " AND p.status=?"
            params.append(status)
        sql += " ORDER BY p.updated_at DESC, p.id DESC"
        return db.all(sql, tuple(params))

    @staticmethod
    def view_project(project_id: int):
        return db.one(_PROJECT_JOIN + " WHERE p.id=?", (project_id,))

    @staticmethod
    def view_project_record(project_id: int):
        return db.one("SELECT * FROM projects WHERE id=?", (project_id,))

    @staticmethod
    def update_project(project_id: int, company_id: int, category_id, title: str, description: str,
                       location: str, budget: float, status: str, image_url: str) -> None:
        db.execute("""UPDATE projects SET company_id=?,category_id=?,title=?,description=?,location=?,
                      budget=?,status=?,image_url=?,updated_at=? WHERE id=?""",
                   (company_id, category_id, title, description, location, budget, status, image_url,
                    datetime.now().isoformat(timespec="seconds"), project_id))

    @staticmethod
    def delete_project(project_id: int) -> None:
        db.execute("DELETE FROM projects WHERE id=?", (project_id,))

    @staticmethod
    def increment_views(project_id: int) -> None:
        db.execute("UPDATE projects SET views=views+1 WHERE id=?", (project_id,))

    @staticmethod
    def view_project_analytics(owner_id: int):
        return db.all("""SELECT p.id,p.title,p.status,p.views,COUNT(f.project_id) shortlist_count
                         FROM projects p JOIN companies c ON c.id=p.company_id
                         LEFT JOIN favourites f ON f.project_id=p.id
                         WHERE c.owner_id=? GROUP BY p.id ORDER BY p.views DESC""", (owner_id,))
