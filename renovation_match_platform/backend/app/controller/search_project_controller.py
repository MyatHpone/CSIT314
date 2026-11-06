from app.entity.project import Project


class SearchProjectController:
    """Stories 24, 29 and 32: search current / past / public projects."""

    def search_projects(self, keyword: str = "", status: str = ""):
        try:
            return True, Project.search_projects(keyword, status)
        except Exception as e:
            return False, str(e)
