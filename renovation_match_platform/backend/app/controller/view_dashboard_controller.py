from app.entity.project import Project
from app.entity.report import Report


class ViewDashboardController:
    def view_dashboard(self):
        try:
            return True, {"counts": Report.view_platform_counts(),
                          "projects": Project.view_all_projects()[:8]}
        except Exception as e:
            return False, str(e)

    def view_platform_counts(self):
        try:
            return True, Report.view_platform_counts()
        except Exception as e:
            return False, str(e)
