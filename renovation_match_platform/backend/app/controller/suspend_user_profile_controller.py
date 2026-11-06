from app.entity.activity_event import ActivityEvent
from app.entity.user_profile import UserProfile


class SuspendUserProfileController:
    def suspend_user_profile(self, user_id: int):
        try:
            UserProfile.suspend_user_profile(user_id)
            ActivityEvent.log(user_id, "PROFILE_SUSPENDED", "profile", user_id)
            return True, "Your account has been suspended. Contact an administrator if this was a mistake."
        except Exception as e:
            return False, str(e)
