from __future__ import annotations

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.services.database import db


class UserAccount:
    def __init__(self, username: str, email: str, password: str, role: str, full_name: str):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.full_name = full_name

    def create_user_account(self) -> int:
        return db.execute(
            "INSERT INTO users(username,email,password_hash,role,full_name,created_at) VALUES(?,?,?,?,?,?)",
            (self.username, self.email, generate_password_hash(self.password), self.role,
             self.full_name, datetime.now().isoformat(timespec="seconds")))

    @staticmethod
    def view_all_user_accounts():
        return db.all("SELECT id,username,email,role,full_name,status,created_at FROM users ORDER BY id DESC")

    @staticmethod
    def view_user_account(user_id: int):
        return db.one("SELECT * FROM users WHERE id=?", (user_id,))

    @staticmethod
    def search_user_accounts(keyword: str):
        like = f"%{keyword}%"
        return db.all("""SELECT id,username,email,role,full_name,status,created_at FROM users
                         WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ? ORDER BY id DESC""",
                      (like, like, like))

    @staticmethod
    def update_user_account(user_id: int, full_name: str, email: str, role: str, status: str) -> None:
        db.execute("UPDATE users SET full_name=?,email=?,role=?,status=? WHERE id=?",
                   (full_name, email, role, status, user_id))

    @staticmethod
    def suspend_user_account(user_id: int) -> None:
        db.execute("UPDATE users SET status='SUSPENDED' WHERE id=?", (user_id,))

    @staticmethod
    def login_user(username: str, password: str):
        user = db.one("SELECT * FROM users WHERE username=? AND status='ACTIVE'", (username.strip(),))
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None

    @staticmethod
    def logout() -> bool:
        # Session clearing happens in the boundary; this confirms the action at entity level.
        return True
