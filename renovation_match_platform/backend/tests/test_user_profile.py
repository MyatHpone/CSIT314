import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.login_user_account_controller import LoginUserAccountController
from app.controller.create_user_account_controller import CreateUserAccountController
from app.controller.create_user_profile_controller import CreateUserProfileController
from app.controller.update_user_profile_controller import UpdateUserProfileController
from app.controller.view_user_profile_controller import ViewUserProfileController
from app.controller.suspend_user_profile_controller import SuspendUserProfileController
from app.controller.search_user_profile_controller import SearchUserProfileController


class UserProfileTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.admin_id = self.user_id("admin")
        self.customer_id = self.user_id("customer")

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def user_id(self, username):
        return db.one("SELECT id FROM users WHERE username=?", (username,))["id"]

    def count_profiles(self, user_id):
        return db.one("SELECT COUNT(*) n FROM profiles WHERE user_id=?", (user_id,))["n"]

    def new_account_data(self, username, full_name):
        return {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Pass1234!",
            "role": "CUSTOMER",
            "full_name": full_name,
        }

    # #8 Create profile
    def test_UT17_creating_account_also_creates_profile(self):
        # Arrange
        controller = CreateUserAccountController()
        data = self.new_account_data("amy01", "Amy Ong")

        # Act
        ok, new_id = controller.create_user_account(self.admin_id, data)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(self.count_profiles(new_id), 1)

    def test_UT18_profile_cannot_be_created_twice(self):
        # Arrange
        controller = CreateUserProfileController()

        # Act
        ok, result = controller.create_user_profile(self.customer_id)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_profiles(self.customer_id), 1)

    def test_UT19_profile_for_user_that_does_not_exist(self):
        # Arrange
        controller = CreateUserProfileController()

        # Act
        ok, result = controller.create_user_profile(9999)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_profiles(9999), 0)

    # #9 Update profile
    def test_UT20_update_profile_with_valid_change(self):
        # Arrange
        controller = UpdateUserProfileController()

        # Act
        ok, result = controller.update_user_profile(self.customer_id, {"phone": "91234567"})

        # Assert
        self.assertTrue(ok)
        _, profile = ViewUserProfileController().view_user_profile(self.customer_id)
        self.assertEqual(profile["phone"], "91234567")

    def test_UT21_update_profile_that_does_not_exist(self):
        # Arrange
        controller = UpdateUserProfileController()

        # Act
        ok, result = controller.update_user_profile(9999, {"phone": "91234567"})

        # Assert
        self.assertFalse(ok)

    # #10 View profile
    def test_UT22_view_own_profile(self):
        # Arrange
        controller = ViewUserProfileController()

        # Act
        ok, result = controller.view_user_profile(self.customer_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["username"], "customer")

    def test_UT23_view_profile_that_does_not_exist(self):
        # Arrange
        controller = ViewUserProfileController()

        # Act
        ok, result = controller.view_user_profile(9999)

        # Assert
        self.assertFalse(ok)

    # #11 Suspend profile
    def test_UT24_suspend_own_profile(self):
        # Arrange
        controller = SuspendUserProfileController()

        # Act
        ok, result = controller.suspend_user_profile(self.customer_id)

        # Assert
        self.assertTrue(ok)
        login_ok, _ = LoginUserAccountController().login_user("customer", "Customer123!")
        self.assertFalse(login_ok)

    def test_UT25_suspend_already_suspended_profile(self):
        # Arrange
        controller = SuspendUserProfileController()
        controller.suspend_user_profile(self.customer_id)

        # Act
        ok, result = controller.suspend_user_profile(self.customer_id)

        # Assert
        self.assertFalse(ok)

    # #12 Search profile
    def test_UT26_search_with_matching_keyword(self):
        # Arrange
        create = CreateUserAccountController()
        create.create_user_account(self.admin_id, self.new_account_data("mei01", "Mei Lim"))
        create.create_user_account(self.admin_id, self.new_account_data("ken02", "Ken Lim"))
        controller = SearchUserProfileController()

        # Act
        ok, result = controller.search_user_profiles("lim")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 2)
        self.assertEqual({row["username"] for row in result}, {"mei01", "ken02"})

    def test_UT27_search_with_no_match(self):
        # Arrange
        controller = SearchUserProfileController()

        # Act
        ok, result = controller.search_user_profiles("zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()