from app.entity.user_profile import UserProfile


class SearchUserProfileController:
    def search_user_profiles(self, keyword: str):
        try:
            return True, UserProfile.search_user_profiles(keyword)
        except Exception as e:
            return False, str(e)
