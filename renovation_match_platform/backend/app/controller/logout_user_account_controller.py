from app.entity.activity_event import ActivityEvent
from app.entity.user_account import UserAccount


class LogoutUserAccountController:
    def logout_user(self, user_id: int):
        try:
            UserAccount.logout()
            ActivityEvent.log(user_id, "LOGOUT", "user", user_id)
            return True, "You have logged out."
        except Exception as e:
            return False, str(e)
