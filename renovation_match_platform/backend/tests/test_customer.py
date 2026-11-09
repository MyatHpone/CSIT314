import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.login_user_account_controller import LoginUserAccountController
from app.controller.logout_user_account_controller import LogoutUserAccountController
from app.controller.create_project_controller import CreateProjectController
from app.controller.search_project_controller import SearchProjectController
from app.controller.view_project_detail_controller import ViewProjectDetailController
from app.controller.save_favourite_controller import SaveFavouriteController
from app.controller.search_favourite_controller import SearchFavouriteController
from app.controller.compare_favourites_controller import CompareFavouritesController


class CustomerTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.customer = dict(db.one("SELECT * FROM users WHERE username='customer'"))
        self.designer = dict(db.one("SELECT * FROM users WHERE username='designer'"))
        self.company_id = db.one("SELECT id FROM companies WHERE owner_id=? ORDER BY id LIMIT 1",
                                 (self.designer["id"],))["id"]

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def new_project(self, title):
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

    def shortlist_count(self, project_id):
        return db.one("SELECT COUNT(*) n FROM favourites WHERE project_id=?", (project_id,))["n"]

    def total_views(self):
        return db.one("SELECT SUM(views) n FROM projects")["n"]

    # #30 Login
    def test_UT66_customer_login_with_valid_details(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("customer", "Customer123!")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["role"], "CUSTOMER")

    def test_UT67_customer_login_with_wrong_password(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("customer", "wrongpassword")

        # Assert
        self.assertFalse(ok)

    # #31 Logout
    def test_UT68_customer_logout_ends_the_session(self):
        # Arrange
        controller = LogoutUserAccountController()

        # Act
        ok, result = controller.logout_user(self.customer["id"])

        # Assert
        self.assertTrue(ok)

    # #32 Search IDPs
    def test_UT69_search_with_matching_keyword(self):
        # Arrange
        self.new_project("Bright Kitchen")
        self.new_project("Compact Kitchen")
        self.new_project("Classic Kitchen")
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("kitchen")

        # Assert
        self.assertTrue(ok)
        self.assertEqual({row["title"] for row in result},
                         {"Bright Kitchen", "Compact Kitchen", "Classic Kitchen"})

    def test_UT70_search_with_no_match(self):
        # Arrange
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)

    # #33 View IDP
    def test_UT71_view_existing_idp(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen")
        controller = ViewProjectDetailController()

        # Act
        ok, result = controller.view_project(project_id, self.customer)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["project"]["title"], "Zen Kitchen")
        views = db.one("SELECT views FROM projects WHERE id=?", (project_id,))["views"]
        self.assertEqual(views, 1)

    def test_UT72_view_idp_that_does_not_exist(self):
        # Arrange
        controller = ViewProjectDetailController()
        before = self.total_views()

        # Act
        ok, result = controller.view_project(9999, self.customer)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.total_views(), before)

    # #34 Save to favourites
    def test_UT73_save_idp_to_favourites(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen")
        controller = SaveFavouriteController()

        # Act
        ok, result = controller.save_favourite(self.customer["id"], project_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(self.shortlist_count(project_id), 1)

    def test_UT74_saving_again_removes_it(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen")
        controller = SaveFavouriteController()
        controller.save_favourite(self.customer["id"], project_id)

        # Act
        ok, result = controller.save_favourite(self.customer["id"], project_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(self.shortlist_count(project_id), 0)

    def test_UT75_save_idp_that_does_not_exist(self):
        # Arrange
        controller = SaveFavouriteController()

        # Act
        ok, result = controller.save_favourite(self.customer["id"], 9999)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.shortlist_count(9999), 0)

    # #35 Search shortlist
    def test_UT76_search_shortlist_with_matching_keyword(self):
        # Arrange
        save = SaveFavouriteController()
        for title in ("Japandi Loft", "Modern Loft", "Retro Loft"):
            save.save_favourite(self.customer["id"], self.new_project(title))
        controller = SearchFavouriteController()

        # Act
        ok, result = controller.search_favourites(self.customer["id"], "japandi")

        # Assert
        self.assertTrue(ok)
        self.assertEqual([row["title"] for row in result], ["Japandi Loft"])

    def test_UT77_search_shortlist_with_no_match(self):
        # Arrange
        SaveFavouriteController().save_favourite(self.customer["id"], self.new_project("Modern Loft"))
        controller = SearchFavouriteController()

        # Act
        ok, result = controller.search_favourites(self.customer["id"], "zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)

    # #36 Compare shortlisted IDPs
    def test_UT78_compare_shortlisted_idps(self):
        # Arrange
        save = SaveFavouriteController()
        save.save_favourite(self.customer["id"], self.new_project("Modern Loft"))
        save.save_favourite(self.customer["id"], self.new_project("Retro Loft"))
        controller = CompareFavouritesController()

        # Act
        ok, result = controller.compare_favourites(self.customer["id"])

        # Assert
        self.assertTrue(ok)
        self.assertEqual({row["title"] for row in result}, {"Modern Loft", "Retro Loft"})

    def test_UT79_compare_with_empty_shortlist(self):
        # Arrange
        controller = CompareFavouritesController()

        # Act
        ok, result = controller.compare_favourites(self.customer["id"])

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()