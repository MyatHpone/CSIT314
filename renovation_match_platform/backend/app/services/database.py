"""Database service: owns the SQLite connection, schema creation, seed data
and the small query helpers used by the Entity layer (same role as
supabase_client.py in the SDM skeleton)."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from werkzeug.security import generate_password_hash

from app.config import DATABASE


class Database:
    """Owns SQLite connections, schema creation, and initial demonstration data."""

    def __init__(self, path: str = DATABASE):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init(self) -> None:
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN
                    ('USER_ADMIN','INTERIOR_DESIGNER','CUSTOMER','PLATFORM_MANAGER')),
                full_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE','SUSPENDED')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                phone TEXT DEFAULT '',
                location TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                address TEXT DEFAULT '',
                website TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL REFERENCES companies(id),
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                budget REAL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'CURRENT'
                    CHECK(status IN ('CURRENT','PAST')),
                image_url TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                views INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS favourites (
                customer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                saved_at TEXT NOT NULL,
                PRIMARY KEY(customer_id, project_id)
            );
            CREATE TABLE IF NOT EXISTS activity_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                event_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                occurred_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_users_role_status ON users(role,status);
            CREATE INDEX IF NOT EXISTS idx_projects_status_category ON projects(status,category_id);
            CREATE INDEX IF NOT EXISTS idx_events_time ON activity_events(occurred_at);
            """)
        self.seed_if_empty()

    def seed_if_empty(self) -> None:
        with self.connect() as db:
            if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
                return
            now = datetime.now().isoformat(timespec="seconds")
            demo_users = [
                ("admin", "admin@example.com", "Admin123!", "USER_ADMIN", "System Admin"),
                ("designer", "designer@example.com", "Design123!", "INTERIOR_DESIGNER", "Demo Designer"),
                ("customer", "customer@example.com", "Customer123!", "CUSTOMER", "Demo Customer"),
                ("manager", "manager@example.com", "Manager123!", "PLATFORM_MANAGER", "Platform Manager"),
            ]
            for username, email, password, role, name in demo_users:
                db.execute("""INSERT INTO users(username,email,password_hash,role,full_name,created_at)
                              VALUES(?,?,?,?,?,?)""",
                           (username, email, generate_password_hash(password), role, name, now))
                uid = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
                db.execute("INSERT INTO profiles(user_id,updated_at) VALUES(?,?)", (uid, now))
            designer_id = db.execute("SELECT id FROM users WHERE username='designer'").fetchone()[0]
            # Seed 100 companies, 100 categories, and 100 projects so the demo has
            # sufficiently large data sets for browsing and report demonstrations.
            for i in range(1, 101):
                db.execute("""INSERT INTO companies(owner_id,name,description,phone,email,address,website,created_at,updated_at)
                              VALUES(?,?,?,?,?,?,?,?,?)""",
                           (designer_id, f"Studio {i:03d}", f"Interior design studio profile {i}",
                            f"+65 6000 {i:04d}", f"studio{i}@example.com",
                            f"{i} Design Avenue, Singapore", "", now, now))
                db.execute("INSERT INTO categories(name,description,created_at) VALUES(?,?,?)",
                           (f"Style Category {i:03d}", f"Demonstration category {i}", now))
            company_ids = [r[0] for r in db.execute("SELECT id FROM companies ORDER BY id").fetchall()]
            category_ids = [r[0] for r in db.execute("SELECT id FROM categories ORDER BY id").fetchall()]
            styles = ["Modern", "Scandinavian", "Minimalist", "Industrial", "Japandi"]
            for i in range(1, 101):
                db.execute("""INSERT INTO projects(company_id,category_id,title,description,location,budget,status,created_at,updated_at,views)
                              VALUES(?,?,?,?,?,?,?,?,?,?)""",
                           (company_ids[i-1], category_ids[i-1],
                            f"{styles[(i-1) % len(styles)]} Home Project {i:03d}",
                            f"Sample portfolio project {i}. Includes design concept and completed-work notes.",
                            ["Central", "East", "North", "West", "North-East"][(i-1) % 5],
                            float(20000 + i * 850), "CURRENT" if i % 3 else "PAST", now, now, i % 37))
            db.commit()

    # ---- query helpers used by the entity classes (parameterised SQL only) ----
    def configure(self, path: str) -> None:
        self.path = path

    def one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchone()

    def all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


db = Database()
