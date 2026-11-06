from app.entity.activity_event import ActivityEvent
from app.entity.user_account import UserAccount


class LoginUserAccountController:
    def login_user(self, username: str, password: str):
        try:
            account = UserAccount.login_user(username, password)
            if not account:
                return False, "Invalid username/password or account is suspended."
            ActivityEvent.log(account["id"], "LOGIN", "user", account["id"])
            return True, account
        except Exception as e:
            return False, str(e)
