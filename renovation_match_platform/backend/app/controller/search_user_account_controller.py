from app.entity.user_account import UserAccount


class SearchUserAccountController:
    def search_user_accounts(self, keyword: str):
        try:
            return True, UserAccount.search_user_accounts(keyword)
        except Exception as e:
            return False, str(e)
