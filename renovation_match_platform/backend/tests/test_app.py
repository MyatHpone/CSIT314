import os
import tempfile
import unittest

from app.main import create_app
from app.services.database import db


class RenovationMatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "test.db")
        self.app = create_app({
            "TESTING": True,
            "DATABASE": self.db_path,
            "SECRET_KEY": "test-only-secret",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def login(self, username, password):
        return self.client.post("/login", data={"username": username, "password": password},
                                follow_redirects=True)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_login_and_dashboard(self):
        response = self.login("customer", "Customer123!")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard", response.data)

    def test_bad_password_is_rejected(self):
        response = self.login("customer", "wrong")
        self.assertIn(b"Invalid username/password", response.data)

    def test_logout_clears_session(self):
        self.login("customer", "Customer123!")
        self.client.post("/logout", follow_redirects=True)
        self.assertEqual(self.client.get("/shortlist").status_code, 302)

    def test_customer_cannot_open_admin_user_page(self):
        self.login("customer", "Customer123!")
        self.assertEqual(self.client.get("/users").status_code, 403)

    def test_seed_data_size(self):
        self.assertEqual(db.one("SELECT COUNT(*) n FROM companies")["n"], 100)
        self.assertEqual(db.one("SELECT COUNT(*) n FROM categories")["n"], 100)
        self.assertEqual(db.one("SELECT COUNT(*) n FROM projects")["n"], 100)

    def test_project_search_api(self):
        response = self.client.get("/api/projects?q=Home")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_project_search_page(self):
        response = self.client.get("/projects/search?q=Scandinavian&status=PAST")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Scandinavian", response.data)

    def test_project_detail_increments_views(self):
        before = db.one("SELECT views FROM projects WHERE id=1")["views"]
        self.assertEqual(self.client.get("/projects/1").status_code, 200)
        self.assertEqual(db.one("SELECT views FROM projects WHERE id=1")["views"], before + 1)
        self.assertEqual(self.client.get("/projects/99999").status_code, 404)

    def test_customer_can_shortlist_project(self):
        self.login("customer", "Customer123!")
        response = self.client.post("/projects/1/favourite", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        customer = db.one("SELECT id FROM users WHERE username='customer'")["id"]
        self.assertIsNotNone(db.one("SELECT 1 FROM favourites WHERE customer_id=? AND project_id=1", (customer,)))
        self.assertEqual(self.client.get("/shortlist/search?q=Home").status_code, 200)
        self.assertEqual(self.client.get("/compare").status_code, 200)

    def test_suspended_account_cannot_login(self):
        uid = db.one("SELECT id FROM users WHERE username='customer'")["id"]
        db.execute("UPDATE users SET status='SUSPENDED' WHERE id=?", (uid,))
        self.assertIn(b"Invalid username/password", self.login("customer", "Customer123!").data)

    def test_admin_creates_updates_and_suspends_account(self):
        self.login("admin", "Admin123!")
        self.client.post("/users/new", data={"username": "newbie", "email": "n@example.com",
                                             "password": "Passw0rd!", "role": "CUSTOMER", "full_name": "New Bie"})
        row = db.one("SELECT id FROM users WHERE username='newbie'")
        self.assertIsNotNone(row)
        self.assertIsNotNone(db.one("SELECT 1 FROM profiles WHERE user_id=?", (row["id"],)))
        self.client.post(f"/users/{row['id']}/edit", data={"full_name": "Renamed", "role": "CUSTOMER", "status": "ACTIVE"})
        self.assertEqual(db.one("SELECT full_name FROM users WHERE id=?", (row["id"],))["full_name"], "Renamed")
        self.assertIn(b"newbie", self.client.get("/users/search?q=newbie").data)
        self.client.post(f"/users/{row['id']}/suspend")
        self.assertEqual(db.one("SELECT status FROM users WHERE id=?", (row["id"],))["status"], "SUSPENDED")

    def test_designer_cannot_edit_other_designers_company(self):
        self.login("admin", "Admin123!")
        self.client.post("/users/new", data={"username": "other", "email": "o@example.com",
                                             "password": "Passw0rd!", "role": "INTERIOR_DESIGNER", "full_name": "Other"})
        self.client.post("/logout")
        self.login("other", "Passw0rd!")
        self.assertEqual(self.client.get("/companies/1/edit").status_code, 403)

    def test_manager_category_crud_and_report(self):
        self.login("manager", "Manager123!")
        self.client.post("/categories/new", data={"name": "Zen", "description": "calm"})
        cat = db.one("SELECT id FROM categories WHERE name='Zen'")
        self.assertIsNotNone(cat)
        self.assertIn(b"Zen", self.client.get("/categories/search?q=Zen").data)
        self.client.post(f"/categories/{cat['id']}/delete")
        self.assertIsNone(db.one("SELECT id FROM categories WHERE name='Zen'"))
        response = self.client.post("/reports", data={"period": "monthly", "selected": "2026-01-15"})
        self.assertEqual(response.status_code, 200)


class ArchitectureTests(unittest.TestCase):
    """Guards the Boundary -> Controller -> Entity layering used by the SDM skeleton."""

    APP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")

    def sources(self, layer):
        folder = os.path.join(self.APP_DIR, layer)
        for name in sorted(os.listdir(folder)):
            if name.endswith(".py") and name != "__init__.py":
                with open(os.path.join(folder, name), encoding="utf-8") as fh:
                    yield name, fh.read()

    def test_boundary_does_not_touch_entities_or_database(self):
        for name, src in self.sources("boundary"):
            self.assertNotIn("app.entity", src, name)
            self.assertNotIn("app.services.database", src, name)

    def test_controller_has_no_web_framework_code(self):
        for name, src in self.sources("controller"):
            self.assertNotIn("flask", src, name)

    def test_entity_does_not_import_upper_layers(self):
        for name, src in self.sources("entity"):
            self.assertNotIn("app.controller", src, name)
            self.assertNotIn("app.boundary", src, name)
            self.assertNotIn("flask", src.replace("werkzeug", ""), name)


if __name__ == "__main__":
    unittest.main()
