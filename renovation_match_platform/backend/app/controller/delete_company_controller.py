from app.controller.view_company_controller import ViewCompanyController
from app.entity.activity_event import ActivityEvent
from app.entity.company import Company


class DeleteCompanyController:
    def delete_company(self, actor: dict, company_id: int):
        try:
            ok, result = ViewCompanyController().view_company(actor, company_id)
            if not ok:
                return False, result
            if Company.has_projects(company_id):
                return False, "Company cannot be deleted while it has projects. Delete or reassign its projects first."
            Company.delete_company(company_id)
            ActivityEvent.log(actor["id"], "COMPANY_DELETED", "company", company_id)
            return True, "Company deleted."
        except Exception as e:
            return False, str(e)
