from __future__ import annotations

from datetime import datetime

from app.services.database import db


class UserProfile:
    def __init__(self, user_id: int, phone: str = "", location: str = "", bio: str = ""):
        self.user_id = user_id
        self.phone = phone
        self.location = location
        self.bio = bio

    def create_user_profile(self) -> int:
        return db.execute("INSERT INTO profiles(user_id,phone,location,bio,updated_at) VALUES(?,?,?,?,?)",
                          (self.user_id, self.phone, self.location, self.bio,
                           datetime.now().isoformat(timespec="seconds")))

    @staticmethod
    def view_user_profile(user_id: int):
        return db.one("""SELECT u.username,u.email,u.full_name,u.role,p.phone,p.location,p.bio,p.updated_at
                         FROM users u JOIN profiles p ON p.user_id=u.id WHERE u.id=?""", (user_id,))

    @staticmethod
    def search_user_profiles(keyword: str):
        like = f"%{keyword}%"
        return db.all("""SELECT u.id,u.username,u.full_name,u.role,u.status,p.location
                         FROM users u JOIN profiles p ON p.user_id=u.id
                         WHERE u.username LIKE ? OR u.full_name LIKE ? OR p.location LIKE ?
                         ORDER BY u.full_name""", (like, like, like))

    @staticmethod
    def update_user_profile(user_id: int, phone: str, location: str, bio: str) -> None:
        db.execute("UPDATE profiles SET phone=?,location=?,bio=?,updated_at=? WHERE user_id=?",
                   (phone, location, bio, datetime.now().isoformat(timespec="seconds"), user_id))

    @staticmethod
    def suspend_user_profile(user_id: int) -> None:
        db.execute("UPDATE users SET status='SUSPENDED' WHERE id=?", (user_id,))
