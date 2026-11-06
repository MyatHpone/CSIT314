from flask import Blueprint, jsonify, request

from app.controller.search_project_controller import SearchProjectController
from app.controller.view_dashboard_controller import ViewDashboardController
from app.controller.view_project_detail_controller import ViewProjectDetailController
from app.services.auth import roles_required

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/health")
def api_health():
    return jsonify(status="ok", application="Renovation Match Platform")


@bp.get("/projects")
def api_projects():
    success, result = SearchProjectController().search_projects(request.args.get("q", ""),
                                                                request.args.get("status", ""))
    if success:
        return jsonify([dict(r) for r in result])
    return jsonify(error=result), 500


@bp.get("/projects/<int:project_id>")
def api_project(project_id: int):
    success, result = ViewProjectDetailController().view_project(project_id, record_view=False)
    if success:
        return jsonify(dict(result["project"]))
    return jsonify(error="Project not found"), 404


@bp.get("/metrics")
@roles_required("INTERIOR_DESIGNER", "PLATFORM_MANAGER", "USER_ADMIN")
def api_metrics():
    success, result = ViewDashboardController().view_platform_counts()
    if success:
        return jsonify(result)
    return jsonify(error=result), 500
