from app.entity.project import Project


class ViewProjectAnalyticsController:
    """Stories 37 and 38: per-project view counts and shortlist counts."""

    def view_project_analytics(self, owner_id: int):
        try:
            return True, Project.view_project_analytics(owner_id)
        except Exception as e:
            return False, str(e)
