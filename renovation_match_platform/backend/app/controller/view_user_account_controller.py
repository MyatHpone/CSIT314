from app.entity.user_account import UserAccount
from app.services.results import NOT_FOUND


class ViewUserAccountController:
    def view_all_user_accounts(self):
        try:
            return True, UserAccount.view_all_user_accounts()
        except Exception as e:
            return False, str(e)

    def view_user_account(self, user_id: int):
        try:
            account = UserAccount.view_user_account(user_id)
            if not account:
                return False, NOT_FOUND
            return True, account
        except Exception as e:
            return False, str(e)
