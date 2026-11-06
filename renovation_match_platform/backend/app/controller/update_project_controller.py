from app.entity.activity_event import ActivityEvent
from app.entity.company import Company
from app.entity.project import Project
from app.services.results import FORBIDDEN, NOT_FOUND
from app.services.validators import validate_project


def _check_access(actor: dict, project_id: int):
    project = Project.view_project_record(project_id)
    if not project:
        return False, NOT_FOUND
    if actor["role"] == "INTERIOR_DESIGNER" and not Company.is_owned_by(project["company_id"], actor["id"]):
        return False, FORBIDDEN
    return True, project


class UpdateProjectController:
    def view_project_for_edit(self, actor: dict, project_id: int):
        try:
            return _check_access(actor, project_id)
        except Exception as e:
            return False, str(e)

    def update_project(self, actor: dict, project_id: int, data: dict):
        try:
            ok, result = _check_access(actor, project_id)
            if not ok:
                return False, result
            clean = validate_project(data)
            if not Company.view_company(clean["company_id"]):
                return False, "Selected company does not exist."
            Project.update_project(project_id, **clean)
            ActivityEvent.log(actor["id"], "PROJECT_UPDATED", "project", project_id)
            return True, "Project updated."
        except Exception as e:
            return False, str(e)
