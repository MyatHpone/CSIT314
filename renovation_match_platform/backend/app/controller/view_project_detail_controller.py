from app.entity.activity_event import ActivityEvent
from app.entity.favourite import Favourite
from app.entity.project import Project
from app.services.results import NOT_FOUND


class ViewProjectDetailController:
    """Story 33: view project details; every visit counts as a view."""

    def view_project(self, project_id: int, actor: dict | None = None, record_view: bool = True):
        try:
            project = Project.view_project(project_id)
            if not project:
                return False, NOT_FOUND
            if record_view:
                Project.increment_views(project_id)
                ActivityEvent.log(actor["id"] if actor else None, "PROJECT_VIEWED", "project", project_id)
            saved = bool(actor and actor["role"] == "CUSTOMER" and Favourite.is_saved(actor["id"], project_id))
            return True, {"project": project, "saved": saved}
        except Exception as e:
            return False, str(e)
