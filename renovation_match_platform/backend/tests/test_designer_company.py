import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.login_user_account_controller import LoginUserAccountController
from app.controller.logout_user_account_controller import LogoutUserAccountController
from app.controller.create_user_account_controller import CreateUserAccountController
from app.controller.create_company_controller import CreateCompanyController
from app.controller.view_company_controller import ViewCompanyController
from app.controller.search_company_controller import SearchCompanyController
from app.controller.update_company_controller import UpdateCompanyController
from app.controller.delete_company_controller import DeleteCompanyController
from app.controller.create_project_controller import CreateProjectController
from app.controller.view_project_detail_controller import ViewProjectDetailController
from app.controller.save_favourite_controller import SaveFavouriteController
from app.controller.view_project_analytics_controller import ViewProjectAnalyticsController


class DesignerCompanyTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.admin_id = self.user_id("admin")
        self.designer = dict(db.one("SELECT * FROM users WHERE username='designer'"))
        self.company_id = db.one("SELECT id FROM companies WHERE owner_id=? ORDER BY id LIMIT 1",
                                 (self.designer["id"],))["id"]

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def user_id(self, username):
        return db.one("SELECT id FROM users WHERE username=?", (username,))["id"]

    def count_companies(self):
        return db.one("SELECT COUNT(*) n FROM companies")["n"]

    def company_data(self, name="Tan Design Studio", phone="6123 4567"):
        return {
            "name": name,
            "description": "Modern HDB and condo interiors",
            "phone": phone,
            "email": "hello@tandesign.example.com",
            "address": "10 Design Avenue, Singapore",
            "website": "",
        }

    def new_company(self, name="Tan Design Studio"):
        CreateCompanyController().create_company(self.designer["id"], self.company_data(name))
        return db.one("SELECT id FROM companies WHERE name=?", (name,))["id"]

    def new_project(self, title="Analytics Kitchen"):
        CreateProjectController().create_project(self.designer, {
            "company_id": self.company_id,
            "category_id": 1,
            "title": title,
            "description": "Test project",
            "location": "East",
            "budget": "30000",
            "status": "CURRENT",
        })
        return db.one("SELECT id FROM projects WHERE title=?", (title,))["id"]

    def analytics_for(self, project_id):
        ok, rows = ViewProjectAnalyticsController().view_project_analytics(self.designer["id"])
        for row in rows:
            if row["id"] == project_id:
                return row
        return None

    # #13 Login
    def test_UT28_designer_login_with_valid_details(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("designer", "Design123!")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["role"], "INTERIOR_DESIGNER")

    def test_UT29_designer_login_with_wrong_password(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("designer", "wrongpassword")

        # Assert
        self.assertFalse(ok)

    # #14 Logout
    def test_UT30_designer_logout_ends_the_session(self):
        # Arrange
        controller = LogoutUserAccountController()

        # Act
        ok, result = controller.logout_user(self.designer["id"])

        # Assert
        self.assertTrue(ok)

    # #15 Create company
    def test_UT31_create_company_with_valid_details(self):
        # Arrange
        controller = CreateCompanyController()

        # Act
        ok, result = controller.create_company(self.designer["id"], self.company_data())

        # Assert
        self.assertTrue(ok)
        company = db.one("SELECT * FROM companies WHERE name='Tan Design Studio'")
        self.assertEqual(company["owner_id"], self.designer["id"])

    def test_UT32_company_name_empty(self):
        # Arrange
        controller = CreateCompanyController()
        before = self.count_companies()

        # Act
        ok, result = controller.create_company(self.designer["id"], self.company_data(name=""))

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_companies(), before)

    # #16 View company
    def test_UT33_view_existing_company(self):
        # Arrange
        controller = ViewCompanyController()

        # Act
        ok, result = controller.view_company(self.designer, self.company_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["id"], self.company_id)

    def test_UT34_view_company_that_does_not_exist(self):
        # Arrange
        controller = ViewCompanyController()

        # Act
        ok, result = controller.view_company(self.designer, 9999)

        # Assert
        self.assertFalse(ok)

    # #17 Search company
    def test_UT35_search_with_matching_keyword(self):
        # Arrange
        self.new_company("Tan Design Studio")
        controller = SearchCompanyController()

        # Act
        ok, result = controller.search_companies(self.designer, "Tan")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Tan Design Studio")

    def test_UT36_search_with_no_match(self):
        # Arrange
        controller = SearchCompanyController()

        # Act
        ok, result = controller.search_companies(self.designer, "zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)

    # #18 Update company
    def test_UT37_update_company_with_valid_change(self):
        # Arrange
        company_id = self.new_company()
        controller = UpdateCompanyController()

        # Act
        ok, result = controller.update_company(
            self.designer, company_id, self.company_data(phone="6999 8888"))

        # Assert
        self.assertTrue(ok)
        _, company = ViewCompanyController().view_company(self.designer, company_id)
        self.assertEqual(company["phone"], "6999 8888")

    def test_UT38_update_company_that_does_not_exist(self):
        # Arrange
        controller = UpdateCompanyController()

        # Act
        ok, result = controller.update_company(self.designer, 9999, self.company_data())

        # Assert
        self.assertFalse(ok)

    def test_UT100_update_company_with_empty_name(self):
        # Arrange
        company_id = self.new_company("Tan Design Studio")
        controller = UpdateCompanyController()

        # Act
        ok, result = controller.update_company(self.designer, company_id, self.company_data(name=""))

        # Assert
        self.assertFalse(ok)
        _, company = ViewCompanyController().view_company(self.designer, company_id)
        self.assertEqual(company["name"], "Tan Design Studio")

    # #19 Delete company
    def test_UT39_delete_existing_company(self):
        # Arrange
        company_id = self.new_company("Empty Studio")
        controller = DeleteCompanyController()

        # Act
        ok, result = controller.delete_company(self.designer, company_id)

        # Assert
        self.assertTrue(ok)
        view_ok, _ = ViewCompanyController().view_company(self.designer, company_id)
        self.assertFalse(view_ok)

    def test_UT40_delete_company_that_does_not_exist(self):
        # Arrange
        controller = DeleteCompanyController()

        # Act
        ok, result = controller.delete_company(self.designer, 9999)

        # Assert
        self.assertFalse(ok)

    # #37 View count
    def test_UT41_view_count_matches_the_views(self):
        # Arrange
        project_id = self.new_project()
        for _ in range(3):
            ViewProjectDetailController().view_project(project_id)

        # Act
        row = self.analytics_for(project_id)

        # Assert
        self.assertEqual(row["views"], 3)

    def test_UT42_idp_never_viewed(self):
        # Arrange
        project_id = self.new_project()

        # Act
        row = self.analytics_for(project_id)

        # Assert
        self.assertEqual(row["views"], 0)

    # #38 Shortlist count
    def test_UT43_shortlist_count_matches_the_saves(self):
        # Arrange
        project_id = self.new_project()
        ok, second_customer = CreateUserAccountController().create_user_account(self.admin_id, {
            "username": "amy01",
            "email": "amy@example.com",
            "password": "Pass1234!",
            "role": "CUSTOMER",
            "full_name": "Amy Ong",
        })
        SaveFavouriteController().save_favourite(self.user_id("customer"), project_id)
        SaveFavouriteController().save_favourite(second_customer, project_id)

        # Act
        row = self.analytics_for(project_id)

        # Assert
        self.assertEqual(row["shortlist_count"], 2)

    def test_UT44_idp_never_shortlisted(self):
        # Arrange
        project_id = self.new_project()

        # Act
        row = self.analytics_for(project_id)

        # Assert
        self.assertEqual(row["shortlist_count"], 0)


if __name__ == "__main__":
    unittest.main()