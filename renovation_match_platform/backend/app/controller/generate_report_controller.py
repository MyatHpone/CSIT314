from app.entity.report import Report


class GenerateReportController:
    """Stories 44-46: daily, weekly and monthly platform reports."""

    def generate_report(self, period: str, selected: str):
        try:
            return True, Report.generate_report(period, selected)
        except (ValueError, TypeError):
            return False, "Enter a valid date / week start / month."
        except Exception as e:
            return False, str(e)
