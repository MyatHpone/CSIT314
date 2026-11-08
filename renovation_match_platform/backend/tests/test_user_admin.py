import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.login_user_account_controller import LoginUserAccountController
from app.controller.logout_user_account_controller import LogoutUserAccountController
from app.controller.create_user_account_controller import CreateUserAccountController
from app.controller.update_user_account_controller import UpdateUserAccountController
from app.controller.view_user_account_controller import ViewUserAccountController
from app.controller.suspend_user_account_controller import SuspendUserAccountController
from app.controller.search_user_account_controller import SearchUserAccountController


class UserAdminTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.admin_id = self.user_id("admin")

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def user_id(self, username):
        return db.one("SELECT id FROM users WHERE username=?", (username,))["id"]

    def count_users(self, username):
        return db.one("SELECT COUNT(*) n FROM users WHERE username=?", (username,))["n"]

    def new_account_data(self, username="amy01", email="amy@example.com"):
        return {
            "username": username,
            "email": email,
            "password": "Pass1234!",
            "role": "CUSTOMER",
            "full_name": "Amy Ong",
        }

    # #1 Login
    def test_UT01_login_with_valid_details(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("admin", "Admin123!")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["role"], "USER_ADMIN")

    def test_UT02_login_with_wrong_password(self):
        # Arrange
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("admin", "wrongpassword")

        # Assert
        self.assertFalse(ok)
        self.assertEqual(result, "Invalid username/password or account is suspended.")

    def test_UT03_suspended_account_cannot_log_in(self):
        # Arrange
        customer_id = self.user_id("customer")
        SuspendUserAccountController().suspend_user_account(self.admin_id, customer_id)
        controller = LoginUserAccountController()

        # Act
        ok, result = controller.login_user("customer", "Customer123!")

        # Assert
        self.assertFalse(ok)

    # #2 Logout
    def test_UT04_logout_ends_the_session(self):
        # Arrange
        controller = LogoutUserAccountController()

        # Act
        ok, result = controller.logout_user(self.admin_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result, "You have logged out.")

    def test_UT05_logout_when_not_logged_in(self):
        # Arrange
        controller = LogoutUserAccountController()

        # Act
        ok, result = controller.logout_user(None)

        # Assert
        self.assertTrue(ok)

    # #3 Create account
    def test_UT06_create_account_with_valid_details(self):
        # Arrange
        controller = CreateUserAccountController()
        data = self.new_account_data()

        # Act
        ok, result = controller.create_user_account(self.admin_id, data)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result, self.user_id("amy01"))

    def test_UT07_duplicate_username_rejected(self):
        # Arrange
        controller = CreateUserAccountController()
        data = self.new_account_data(username="customer", email="other@example.com")

        # Act
        ok, result = controller.create_user_account(self.admin_id, data)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_users("customer"), 1)

    def test_UT08_empty_required_field_rejected(self):
        # Arrange
        controller = CreateUserAccountController()
        data = self.new_account_data(email="")

        # Act
        ok, result = controller.create_user_account(self.admin_id, data)

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_users("amy01"), 0)

    # #4 Update account
    def test_UT09_update_account_with_valid_change(self):
        # Arrange
        controller = UpdateUserAccountController()
        customer_id = self.user_id("customer")

        # Act
        ok, result = controller.update_user_account(
            self.admin_id, customer_id, {"email": "new.customer@example.com"})

        # Assert
        self.assertTrue(ok)
        _, account = ViewUserAccountController().view_user_account(customer_id)
        self.assertEqual(account["email"], "new.customer@example.com")

    def test_UT10_update_account_that_does_not_exist(self):
        # Arrange
        controller = UpdateUserAccountController()

        # Act
        ok, result = controller.update_user_account(
            self.admin_id, 9999, {"email": "ghost@example.com"})

        # Assert
        self.assertFalse(ok)

    # #5 View account
    def test_UT11_view_existing_account(self):
        # Arrange
        controller = ViewUserAccountController()
        customer_id = self.user_id("customer")

        # Act
        ok, result = controller.view_user_account(customer_id)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(result["username"], "customer")

    def test_UT12_view_account_that_does_not_exist(self):
        # Arrange
        controller = ViewUserAccountController()

        # Act
        ok, result = controller.view_user_account(9999)

        # Assert
        self.assertFalse(ok)

    # #6 Suspend account
    def test_UT13_suspend_active_account(self):
        # Arrange
        controller = SuspendUserAccountController()
        customer_id = self.user_id("customer")

        # Act
        ok, result = controller.suspend_user_account(self.admin_id, customer_id)

        # Assert
        self.assertTrue(ok)
        _, account = ViewUserAccountController().view_user_account(customer_id)
        self.assertEqual(account["status"], "SUSPENDED")

    def test_UT14_suspend_account_that_does_not_exist(self):
        # Arrange
        controller = SuspendUserAccountController()

        # Act
        ok, result = controller.suspend_user_account(self.admin_id, 9999)

        # Assert
        self.assertFalse(ok)

    # #7 Search account
    def test_UT15_search_with_matching_keyword(self):
        # Arrange
        create = CreateUserAccountController()
        create.create_user_account(self.admin_id, self.new_account_data("tanmei", "mei@example.com"))
        create.create_user_account(self.admin_id, self.new_account_data("jtan88", "jay@example.com"))
        controller = SearchUserAccountController()

        # Act
        ok, result = controller.search_user_accounts("tan")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 2)
        self.assertEqual({row["username"] for row in result}, {"tanmei", "jtan88"})

    def test_UT16_search_with_no_match(self):
        # Arrange
        controller = SearchUserAccountController()

        # Act
        ok, result = controller.search_user_accounts("zzz")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()