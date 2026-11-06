import sqlite3

from app.config import ROLES
from app.controller.create_user_profile_controller import CreateUserProfileController
from app.entity.activity_event import ActivityEvent
from app.entity.user_account import UserAccount


class CreateUserAccountController:
    def create_user_account(self, actor_id: int, data: dict):
        try:
            required = ["username", "email", "password", "role", "full_name"]
            if any(not str(data.get(k, "")).strip() for k in required):
                return False, "All fields are required."
            if len(data["password"]) < 8:
                return False, "Password must contain at least 8 characters."
            if data["role"] not in ROLES:
                return False, "Choose a valid role."

            account = UserAccount(data["username"].strip(), data["email"].strip().lower(),
                                  data["password"], data["role"], data["full_name"].strip())
            try:
                user_id = account.create_user_account()
            except sqlite3.IntegrityError:
                return False, "Username or email already exists."

            ok, error = CreateUserProfileController().create_user_profile(user_id)
            if not ok:
                return False, error
            ActivityEvent.log(actor_id, "USER_CREATED", "user", user_id)
            return True, user_id
        except Exception as e:
            return False, str(e)
