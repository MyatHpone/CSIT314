from app.entity.activity_event import ActivityEvent
from app.entity.user_account import UserAccount
from app.services.results import NOT_FOUND


class SuspendUserAccountController:
    def suspend_user_account(self, actor_id: int, user_id: int):
        try:
            if user_id == actor_id:
                return False, "You cannot suspend your own active admin account."
            if not UserAccount.view_user_account(user_id):
                return False, NOT_FOUND
            UserAccount.suspend_user_account(user_id)
            ActivityEvent.log(actor_id, "USER_SUSPENDED", "user", user_id)
            return True, "User account suspended."
        except Exception as e:
            return False, str(e)
