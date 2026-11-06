"""Renovation Match Platform - Flask entry point (BCE: Boundary / Controller / Entity).

Run from the backend/ folder:   python -m app.main
"""
from __future__ import annotations

import os

from flask import Flask, render_template

from app.config import DATABASE, FRONTEND_DIR, SECRET_KEY
from app.services.auth import current_user, load_current_user
from app.services.database import db

# Auth
from app.boundary.login_user_account_boundary import bp as login_user_account_bp
from app.boundary.logout_user_account_boundary import bp as logout_user_account_bp
from app.boundary.view_dashboard_boundary import bp as view_dashboard_bp

# User Accounts
from app.boundary.create_user_account_boundary import bp as create_user_account_bp
from app.boundary.view_user_account_boundary import bp as view_user_account_bp
from app.boundary.search_user_account_boundary import bp as search_user_account_bp
from app.boundary.update_user_account_boundary import bp as update_user_account_bp
from app.boundary.suspend_user_account_boundary import bp as suspend_user_account_bp

# User Profiles
from app.boundary.view_user_profile_boundary import bp as view_user_profile_bp
from app.boundary.update_user_profile_boundary import bp as update_user_profile_bp
from app.boundary.search_user_profile_boundary import bp as search_user_profile_bp
from app.boundary.suspend_user_profile_boundary import bp as suspend_user_profile_bp

# Companies
from app.boundary.create_company_boundary import bp as create_company_bp
from app.boundary.view_company_boundary import bp as view_company_bp
from app.boundary.search_company_boundary import bp as search_company_bp
from app.boundary.update_company_boundary import bp as update_company_bp
from app.boundary.delete_company_boundary import bp as delete_company_bp

# Projects
from app.boundary.create_project_boundary import bp as create_project_bp
from app.boundary.view_project_boundary import bp as view_project_bp
from app.boundary.search_project_boundary import bp as search_project_bp
from app.boundary.view_project_detail_boundary import bp as view_project_detail_bp
from app.boundary.update_project_boundary import bp as update_project_bp
from app.boundary.delete_project_boundary import bp as delete_project_bp
from app.boundary.view_project_analytics_boundary import bp as view_project_analytics_bp

# Favourites
from app.boundary.save_favourite_boundary import bp as save_favourite_bp
from app.boundary.view_favourites_boundary import bp as view_favourites_bp
from app.boundary.search_favourite_boundary import bp as search_favourite_bp
from app.boundary.compare_favourites_boundary import bp as compare_favourites_bp

# Categories
from app.boundary.create_category_boundary import bp as create_category_bp
from app.boundary.view_category_boundary import bp as view_category_bp
from app.boundary.search_category_boundary import bp as search_category_bp
from app.boundary.update_category_boundary import bp as update_category_bp
from app.boundary.delete_category_boundary import bp as delete_category_bp

# Reports (Platform Manager)
from app.boundary.generate_report_boundary import bp as generate_report_bp
# JSON API
from app.boundary.api_boundary import bp as api_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__,
                template_folder=str(FRONTEND_DIR / "templates"),
                static_folder=str(FRONTEND_DIR / "static"))
    app.config.update(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE)
    if test_config:
        app.config.update(test_config)

    db.configure(app.config["DATABASE"])
    db.init()

    app.before_request(load_current_user)

    @app.context_processor
    def inject_user():
        return {"current_user": current_user()}

    # Auth
    app.register_blueprint(login_user_account_bp)
    app.register_blueprint(logout_user_account_bp)
    app.register_blueprint(view_dashboard_bp)

    # User Accounts
    app.register_blueprint(create_user_account_bp)
    app.register_blueprint(view_user_account_bp)
    app.register_blueprint(search_user_account_bp)
    app.register_blueprint(update_user_account_bp)
    app.register_blueprint(suspend_user_account_bp)

    # User Profiles
    app.register_blueprint(view_user_profile_bp)
    app.register_blueprint(update_user_profile_bp)
    app.register_blueprint(search_user_profile_bp)
    app.register_blueprint(suspend_user_profile_bp)

    # Companies
    app.register_blueprint(create_company_bp)
    app.register_blueprint(view_company_bp)
    app.register_blueprint(search_company_bp)
    app.register_blueprint(update_company_bp)
    app.register_blueprint(delete_company_bp)

    # Projects
    app.register_blueprint(create_project_bp)
    app.register_blueprint(view_project_bp)
    app.register_blueprint(search_project_bp)
    app.register_blueprint(view_project_detail_bp)
    app.register_blueprint(update_project_bp)
    app.register_blueprint(delete_project_bp)
    app.register_blueprint(view_project_analytics_bp)

    # Favourites
    app.register_blueprint(save_favourite_bp)
    app.register_blueprint(view_favourites_bp)
    app.register_blueprint(search_favourite_bp)
    app.register_blueprint(compare_favourites_bp)

    # Categories
    app.register_blueprint(create_category_bp)
    app.register_blueprint(view_category_bp)
    app.register_blueprint(search_category_bp)
    app.register_blueprint(update_category_bp)
    app.register_blueprint(delete_category_bp)

    # Reports (Platform Manager)
    app.register_blueprint(generate_report_bp)
    # JSON API
    app.register_blueprint(api_bp)

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, message="You do not have permission to access this page."), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="The requested record or page was not found."), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1",
            host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")))
