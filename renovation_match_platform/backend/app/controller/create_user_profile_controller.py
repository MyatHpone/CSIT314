from app.entity.user_profile import UserProfile


class CreateUserProfileController:
    """Story 8: a profile is created together with every new user account."""

    def create_user_profile(self, user_id: int):
        try:
            return True, UserProfile(user_id).create_user_profile()
        except Exception as e:
            return False, str(e)
