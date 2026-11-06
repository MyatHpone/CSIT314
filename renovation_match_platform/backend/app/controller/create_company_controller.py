from app.entity.activity_event import ActivityEvent
from app.entity.company import Company


class CreateCompanyController:
    def create_company(self, actor_id: int, data: dict):
        try:
            name = data.get("name", "").strip()
            if not name:
                return False, "Company name is required."
            company = Company(actor_id, name, data.get("description", ""), data.get("phone", ""),
                              data.get("email", ""), data.get("address", ""), data.get("website", ""))
            company_id = company.create_company()
            ActivityEvent.log(actor_id, "COMPANY_CREATED", "company", company_id)
            return True, "Company created."
        except Exception as e:
            return False, str(e)
