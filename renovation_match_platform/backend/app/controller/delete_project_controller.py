from app.controller.update_project_controller import _check_access
from app.entity.activity_event import ActivityEvent
from app.entity.project import Project


class DeleteProjectController:
    def delete_project(self, actor: dict, project_id: int):
        try:
            ok, result = _check_access(actor, project_id)
            if not ok:
                return False, result
            Project.delete_project(project_id)
            ActivityEvent.log(actor["id"], "PROJECT_DELETED", "project", project_id)
            return True, "Project deleted."
        except Exception as e:
            return False, str(e)
