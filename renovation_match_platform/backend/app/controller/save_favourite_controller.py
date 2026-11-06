from app.entity.activity_event import ActivityEvent
from app.entity.favourite import Favourite
from app.entity.project import Project
from app.services.results import NOT_FOUND


class SaveFavouriteController:
    """Story 34: save a project to the shortlist, or remove it if already saved."""

    def save_favourite(self, customer_id: int, project_id: int):
        try:
            if not Project.view_project_record(project_id):
                return False, NOT_FOUND
            favourite = Favourite(customer_id, project_id)
            if Favourite.is_saved(customer_id, project_id):
                favourite.remove_favourite()
                ActivityEvent.log(customer_id, "PROJECT_UNSHORTLISTED", "project", project_id)
                return True, "Project removed from your shortlist."
            favourite.save_favourite()
            ActivityEvent.log(customer_id, "PROJECT_SHORTLISTED", "project", project_id)
            return True, "Project added to your shortlist."
        except Exception as e:
            return False, str(e)
