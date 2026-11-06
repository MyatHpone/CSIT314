from app.entity.user_profile import UserProfile
from app.services.results import NOT_FOUND


class ViewUserProfileController:
    def view_user_profile(self, user_id: int):
        try:
            profile = UserProfile.view_user_profile(user_id)
            if not profile:
                return False, NOT_FOUND
            return True, profile
        except Exception as e:
            return False, str(e)
