from app.controller.view_company_controller import _owner_filter
from app.entity.company import Company


class SearchCompanyController:
    def search_companies(self, actor: dict, keyword: str):
        try:
            return True, Company.search_companies(keyword, _owner_filter(actor))
        except Exception as e:
            return False, str(e)
