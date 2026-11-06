from app.entity.category import Category
from app.entity.company import Company
from app.entity.project import Project


class ViewProjectController:
    """Stories 21 and 26: view current / past projects (filter by status)."""

    def view_projects(self, status: str = ""):
        try:
            return True, Project.view_all_projects(status)
        except Exception as e:
            return False, str(e)

    def view_form_options(self, actor: dict, all_companies: bool = False):
        try:
            owner = None if all_companies or actor["role"] != "INTERIOR_DESIGNER" else actor["id"]
            return True, (Company.view_company_options(owner), Category.view_all_categories())
        except Exception as e:
            return False, str(e)
