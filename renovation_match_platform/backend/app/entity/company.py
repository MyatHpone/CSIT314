from __future__ import annotations

from datetime import datetime

from app.services.database import db


class Company:
    def __init__(self, owner_id: int, name: str, description: str = "", phone: str = "",
                 email: str = "", address: str = "", website: str = ""):
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.phone = phone
        self.email = email
        self.address = address
        self.website = website

    def create_company(self) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        return db.execute("""INSERT INTO companies(owner_id,name,description,phone,email,address,website,created_at,updated_at)
                             VALUES(?,?,?,?,?,?,?,?,?)""",
                          (self.owner_id, self.name, self.description, self.phone, self.email,
                           self.address, self.website, now, now))

    @staticmethod
    def view_all_companies(owner_id: int | None = None):
        if owner_id is None:
            return db.all("SELECT * FROM companies ORDER BY id DESC")
        return db.all("SELECT * FROM companies WHERE owner_id=? ORDER BY id DESC", (owner_id,))

    @staticmethod
    def view_company_options(owner_id: int | None = None):
        if owner_id is None:
            return db.all("SELECT id,name FROM companies ORDER BY name")
        return db.all("SELECT id,name FROM companies WHERE owner_id=? ORDER BY name", (owner_id,))

    @staticmethod
    def search_companies(keyword: str, owner_id: int | None = None):
        like = f"%{keyword}%"
        if owner_id is None:
            return db.all("SELECT * FROM companies WHERE name LIKE ? ORDER BY id DESC", (like,))
        return db.all("SELECT * FROM companies WHERE owner_id=? AND name LIKE ? ORDER BY id DESC",
                      (owner_id, like))

    @staticmethod
    def view_company(company_id: int):
        return db.one("SELECT * FROM companies WHERE id=?", (company_id,))

    @staticmethod
    def is_owned_by(company_id, owner_id: int) -> bool:
        return db.one("SELECT id FROM companies WHERE id=? AND owner_id=?", (company_id, owner_id)) is not None

    @staticmethod
    def has_projects(company_id: int) -> bool:
        return db.one("SELECT id FROM projects WHERE company_id=?", (company_id,)) is not None

    @staticmethod
    def update_company(company_id: int, name: str, description: str, phone: str,
                       email: str, address: str, website: str) -> None:
        db.execute("""UPDATE companies SET name=?,description=?,phone=?,email=?,address=?,website=?,updated_at=?
                      WHERE id=?""",
                   (name, description, phone, email, address, website,
                    datetime.now().isoformat(timespec="seconds"), company_id))

    @staticmethod
    def delete_company(company_id: int) -> None:
        db.execute("DELETE FROM companies WHERE id=?", (company_id,))
