from app.entity.company import Company
from app.services.results import FORBIDDEN, NOT_FOUND


def _owner_filter(actor: dict):
    """Interior designers only see their own companies."""
    return actor["id"] if actor["role"] == "INTERIOR_DESIGNER" else None


class ViewCompanyController:
    def view_all_companies(self, actor: dict):
        try:
            return True, Company.view_all_companies(_owner_filter(actor))
        except Exception as e:
            return False, str(e)

    def view_company(self, actor: dict, company_id: int):
        try:
            company = Company.view_company(company_id)
            if not company:
                return False, NOT_FOUND
            if actor["role"] == "INTERIOR_DESIGNER" and company["owner_id"] != actor["id"]:
                return False, FORBIDDEN
            return True, company
        except Exception as e:
            return False, str(e)
