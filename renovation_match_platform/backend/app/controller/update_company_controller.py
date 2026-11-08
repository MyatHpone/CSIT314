from app.controller.view_company_controller import ViewCompanyController
from app.entity.activity_event import ActivityEvent
from app.entity.company import Company


class UpdateCompanyController:
    def update_company(self, actor: dict, company_id: int, data: dict):
        try:
            ok, result = ViewCompanyController().view_company(actor, company_id)
            if not ok:
                return False, result
            name = data.get("name","").strip()
            if not name:
                return False,"Campany name is required"
            Company.update_company(company_id, data.get("name", "").strip(), data.get("description", ""),
                                   data.get("phone", ""), data.get("email", ""), data.get("address", ""),
                                   data.get("website", ""))
            ActivityEvent.log(actor["id"], "COMPANY_UPDATED", "company", company_id)
            return True, "Company information updated."
        except Exception as e:
            return False, str(e)
