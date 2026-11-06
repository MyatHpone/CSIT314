from app.entity.activity_event import ActivityEvent
from app.entity.user_profile import UserProfile


class UpdateUserProfileController:
    def update_user_profile(self, user_id: int, data: dict):
        try:
            UserProfile.update_user_profile(user_id, data.get("phone", "").strip(),
                                            data.get("location", "").strip(), data.get("bio", "").strip())
            ActivityEvent.log(user_id, "PROFILE_UPDATED", "profile", user_id)
            return True, "Profile updated."
        except Exception as e:
            return False, str(e)
