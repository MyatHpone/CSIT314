import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.login_user_account_controller import LoginUserAccountController
from app.controller.logout_user_account_controller import LogoutUserAccountController
from app.controller.create_category_controller import CreateCategoryController
from app.controller.view_category_controller import ViewCategoryController
from app.controller.update_category_controller import UpdateCategoryController
from app.controller.delete_category_controller import DeleteCategoryController
from app.controller.search_category_controller import SearchCategoryController
from app.controller.generate_report_controller import GenerateReportController


class PlatformManagerTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.manager_id = self.user_id("manager")
        self.customer_id = self.user_id("customer")
        self.company_id = db.one("SELECT id FROM companies ORDER BY id LIMIT 1")["id"]

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def user_id(self, username):
        return db.one("SELECT id FROM users WHERE username=?", (username,))["id"]

    def count_categories(self, name=None):
        if name is None:
            return db.one("SELECT COUNT(*) n FROM categories")["n"]
        return db.one("SELECT COUNT(*) n FROM categories WHERE name=?", (name,))["n"]

    def new_category(self, name, description=""):
        CreateCategoryController().create_category(self.manager_id, {"name": name, "description": description})
        return db.one("SELECT id FROM categories WHERE name=?", (name,))["id"]

    def add_user_on(self, username, day):
        db.execute("""INSERT INTO users(username,email,password_hash,role,full_name,status,created_at)
                      VALUES(?,?,?,?,?,?,?)""",
                   (username, f"{username}@example.com", "x", "CUSTOMER", username, "ACTIVE", f"{day}T10:00:00"))

    def add_project_on(self, title, day, views=0):
        return db.execute("""INSERT INTO projects(company_id,category_id,title,status,created_at,updated_at,views)
                             VALUES(?,?,?,?,?,?,?)""",
                          (self.company_id, 1, title, "CURRENT", f"{day}T10:00:00", f"{day}T10:00:00", views))

    def add_view_on(self, project_id, day):
        db.execute("""INSERT INTO activity_events(actor_id,event_type,entity_type,entity_id,occurred_at)
                      VALUES(?,?,?,?,?)""",
                   (self.customer_id, "PROJECT_VIEWED", "project", project_id, f"{day}T10:00:00"))

    def add_shortlist_on(self, project_id, day):
        db.execute("INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)",
                   (self.customer_id, project_id, f"{day}T10:00:00"))

    # #39 Create category
    def test_UT80_create_category_with_valid_name(self):
        # Arrange
        controller = CreateCategoryController()

        # Act
        ok, result = controller.create_category(self.manager_id, {"name": "Japandi"})

        # Assert
        self.assertTrue(ok)
        self.assertEqual(self.count_categories("Japandi"), 1)

    def test_UT81_duplicate_name_rejected(self):
        # Arrange
        self.new_category("Japandi")
        controller = CreateCategoryController()

        # Act
        ok, result = controller.create_category(self.manager_id, {"name": "Japandi"})

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_categories("Japandi"), 1)

    def test_UT82_empty_name_rejected(self):
        # Arrange
        controller = CreateCategoryController()
        before = self.count_categories()

        # Act
        ok, result = controller.create_category(self.manager_id, {"name": ""})

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_categories(), before)

    # #40 View category
    def test_UT83_view_existing_category(self):
        # Arrange
        category_id = self.new_category("Japandi")
        controller = ViewCategoryController()

        # Act
        ok, result = controller.view_category(category_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["name"], "Japandi")

    def test_UT84_view_category_that_does_not_exist(self):
        # Arrange
        controller = ViewCategoryController()

        # Act
        ok, result = controller.view_category(9999)

        # Assert
        self.assertFalse(ok)

    # #41 Update category
    def test_UT85_update_category_with_valid_change(self):
        # Arrange
        category_id = self.new_category("Japandi")
        controller = UpdateCategoryController()

        # Act
        ok, result = controller.update_category(
            self.manager_id, category_id, {"name": "Japandi", "description": "Warm minimalism"})

        # Assert
        self.assertTrue(ok)
        _, category = ViewCategoryController().view_category(category_id)
        self.assertEqual(category["description"], "Warm minimalism")

    def test_UT86_rename_to_existing_name_rejected(self):
        # Arrange
        self.new_category("Japandi")
        retro_id = self.new_category("Retro")
        controller = UpdateCategoryController()

        # Act
        ok, result = controller.update_category(self.manager_id, retro_id, {"name": "Japandi"})

        # Assert
        self.assertFalse(ok)
        _, category = ViewCategoryController().view_category(retro_id)
        self.assertEqual(category["name"], "Retro")

    # #42 Delete category
    def test_UT87_delete_existing_category(self):
        # Arrange
        category_id = self.new_category("Retro")
        controller = DeleteCategoryController()

        # Act
        ok, result = controller.delete_category(self.manager_id, category_id)

        # Assert
        self.assertTrue(ok)
        view_ok, _ = ViewCategoryController().view_category(category_id)
        self.assertFalse(view_ok)

    def test_UT88_delete_category_that_does_not_exist(self):
        # Arrange
        controller = DeleteCategoryController()

        # Act
        ok, result = controller.delete_category(self.manager_id, 9999)

        # Assert
        self.assertFalse(ok)

    # #43 Search category
    def test_UT89_search_with_matching_keyword(self):
        # Arrange
        self.new_category("Japandi")
        controller = SearchCategoryController()

        # Act
        ok, result = controller.search_categories("Jap")

        # Assert
        self.assertTrue(ok)
        self.assertEqual([row["name"] for row in result], ["Japandi"])

    def test_UT90_search_with_no_match(self):
        # Arrange
        controller = SearchCategoryController()

        # Act
        ok, result = controller.search_categories("zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)

    # #44 Daily report
    def test_UT91_daily_report_counts_only_selected_date(self):
        # Arrange
        self.add_user_on("user_nov04", "2026-11-04")
        self.add_user_on("user_nov05a", "2026-11-05")
        self.add_user_on("user_nov05b", "2026-11-05")
        self.add_user_on("user_nov06", "2026-11-06")
        older_project = self.add_project_on("Viewed Loft", "2026-11-04", views=6)
        new_project = self.add_project_on("New Loft", "2026-11-05")
        for day in ("2026-11-04", "2026-11-04",
                    "2026-11-05", "2026-11-05", "2026-11-05",
                    "2026-11-06"):
            self.add_view_on(older_project, day)
        self.add_shortlist_on(older_project, "2026-11-05")
        self.add_shortlist_on(new_project, "2026-11-06")
        controller = GenerateReportController()

        # Act
        ok, report = controller.generate_report("daily", "2026-11-05")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(report["new_users"], 2)
        self.assertEqual(report["new_projects"], 1)
        self.assertEqual(report["shortlists"], 1)
        self.assertEqual(report["project_views"], 3)

    def test_UT92_daily_report_for_quiet_date(self):
        # Arrange
        controller = GenerateReportController()

        # Act
        ok, report = controller.generate_report("daily", "2020-01-01")

        # Assert
        self.assertTrue(ok)
        for key in ("new_users", "new_projects", "project_views", "shortlists"):
            self.assertEqual(report[key], 0)

    # #45 Weekly report
    def test_UT93_weekly_report_includes_only_selected_week(self):
        # Arrange
        for username, day in (("user_sun01", "2026-11-01"), ("user_mon02", "2026-11-02"),
                              ("user_thu05", "2026-11-05"), ("user_sun08", "2026-11-08"),
                              ("user_mon09", "2026-11-09")):
            self.add_user_on(username, day)
        controller = GenerateReportController()

        # Act
        ok, report = controller.generate_report("weekly", "2026-11-02")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(report["label"], "2026-11-02 to 2026-11-08")
        self.assertEqual(report["new_users"], 3)

    def test_UT94_weekly_report_for_quiet_week(self):
        # Arrange
        controller = GenerateReportController()

        # Act
        ok, report = controller.generate_report("weekly", "2020-01-06")

        # Assert
        self.assertTrue(ok)
        for key in ("new_users", "new_projects", "project_views", "shortlists"):
            self.assertEqual(report[key], 0)

    # #46 Monthly report
    def test_UT95_monthly_report_includes_only_selected_month(self):
        # Arrange
        for username, day in (("user_sep30", "2026-09-30"), ("user_oct01", "2026-10-01"),
                              ("user_oct31", "2026-10-31"), ("user_nov01", "2026-11-01")):
            self.add_user_on(username, day)
        controller = GenerateReportController()

        # Act
        ok, report = controller.generate_report("monthly", "2026-10")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(report["label"], "October 2026")
        self.assertEqual(report["new_users"], 2)

    def test_UT96_invalid_month_rejected(self):
        # Arrange
        controller = GenerateReportController()

        # Act
        ok, result = controller.generate_report("monthly", "2026-13")

        # Assert
        self.assertFalse(ok)
        self.assertEqual(result, "Enter a valid date / week start / month.")

    # #47 Login
    def test_UT97_platform_manager_login_with_valid_details(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("manager", "Manager123!")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["role"], "PLATFORM_MANAGER")

    def test_UT98_platform_manager_login_with_wrong_password(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("manager", "wrongpassword")

        # Assert
        self.assertFalse(ok)

    # #48 Logout
    def test_UT99_platform_manager_logout_ends_the_session(self):
        # Arrange
        controller = LogoutUserAccountController()

        # Act
        ok, result = controller.logout_user(self.manager_id)

        # Assert
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()