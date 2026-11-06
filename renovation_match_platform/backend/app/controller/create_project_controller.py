from app.entity.activity_event import ActivityEvent
from app.entity.company import Company
from app.entity.project import Project
from app.services.validators import validate_project


class CreateProjectController:
    """Stories 20 and 25: a project is current or past depending on its status."""

    def create_project(self, actor: dict, data: dict):
        try:
            if actor["role"] == "INTERIOR_DESIGNER" and not Company.is_owned_by(data.get("company_id"), actor["id"]):
                return False, "Choose a company belonging to your account."
            clean = validate_project(data)
            if not Company.view_company(clean["company_id"]):
                return False, "Selected company does not exist."
            project_id = Project(**clean).create_project()
            ActivityEvent.log(actor["id"], "PROJECT_CREATED", "project", project_id)
            return True, "Project created."
        except Exception as e:
            return False, str(e)
