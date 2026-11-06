from app.config import ACCOUNT_STATUSES, ROLES
from app.entity.activity_event import ActivityEvent
from app.entity.user_account import UserAccount
from app.services.results import NOT_FOUND


class UpdateUserAccountController:
    def update_user_account(self, actor_id: int, user_id: int, data: dict):
        try:
            existing = UserAccount.view_user_account(user_id)
            if not existing:
                return False, NOT_FOUND
            role = data.get("role", existing["role"])
            status = data.get("status", existing["status"])
            if role not in ROLES:
                return False, "Invalid role."
            if status not in ACCOUNT_STATUSES:
                return False, "Invalid status."
            UserAccount.update_user_account(
                user_id,
                data.get("full_name", existing["full_name"]).strip(),
                data.get("email", existing["email"]).strip().lower(),
                role, status)
            ActivityEvent.log(actor_id, "USER_UPDATED", "user", user_id)
            return True, "User account updated."
        except Exception as e:
            return False, str(e)
