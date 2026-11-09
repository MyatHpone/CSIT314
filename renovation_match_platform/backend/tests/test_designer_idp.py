import gc
import os
import tempfile
import unittest

from app.services.database import db
from app.controller.create_project_controller import CreateProjectController
from app.controller.view_project_controller import ViewProjectController
from app.controller.update_project_controller import UpdateProjectController
from app.controller.delete_project_controller import DeleteProjectController
from app.controller.search_project_controller import SearchProjectController


class DesignerIdpTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.configure(os.path.join(self.tmp.name, "test.db"))
        db.init()
        self.designer = dict(db.one("SELECT * FROM users WHERE username='designer'"))
        self.company_id = db.one("SELECT id FROM companies WHERE owner_id=? ORDER BY id LIMIT 1",
                                 (self.designer["id"],))["id"]

    def tearDown(self):
        gc.collect()
        self.tmp.cleanup()

    def count_projects(self):
        return db.one("SELECT COUNT(*) n FROM projects")["n"]

    def project_data(self, title="Zen Kitchen", status="CURRENT",
                     description="Open-plan kitchen", category_id=1):
        return {
            "company_id": self.company_id,
            "category_id": category_id,
            "title": title,
            "description": description,
            "location": "East",
            "budget": "30000",
            "status": status,
        }

    def new_project(self, title="Zen Kitchen", status="CURRENT"):
        CreateProjectController().create_project(self.designer, self.project_data(title, status))
        return db.one("SELECT id FROM projects WHERE title=?", (title,))["id"]

    def view_record(self, project_id):
        return UpdateProjectController().view_project_for_edit(self.designer, project_id)

    # #20 Create current IDP
    def test_UT45_create_idp_with_valid_details(self):
        # Arrange
        controller = CreateProjectController()

        # Act
        ok, result = controller.create_project(self.designer, self.project_data())

        # Assert
        self.assertTrue(ok)
        project = db.one("SELECT * FROM projects WHERE title='Zen Kitchen'")
        self.assertEqual(project["status"], "CURRENT")
        self.assertEqual(project["company_id"], self.company_id)

    def test_UT46_title_empty(self):
        # Arrange
        controller = CreateProjectController()
        before = self.count_projects()

        # Act
        ok, result = controller.create_project(self.designer, self.project_data(title=""))

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_projects(), before)

    def test_UT47_category_does_not_exist(self):
        # Arrange
        controller = CreateProjectController()
        before = self.count_projects()

        # Act
        ok, result = controller.create_project(self.designer, self.project_data(category_id=9999))

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_projects(), before)

    # #21 View current IDPs
    def test_UT48_view_current_idps_only(self):
        # Arrange
        controller = ViewProjectController()

        # Act
        ok, result = controller.view_projects("CURRENT")

        # Assert
        self.assertTrue(ok)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(row["status"] == "CURRENT" for row in result))

    def test_UT49_new_current_idp_appears_in_list(self):
        # Arrange
        self.new_project("Zen Kitchen", "CURRENT")
        controller = ViewProjectController()

        # Act
        ok, result = controller.view_projects("CURRENT")

        # Assert
        self.assertTrue(ok)
        self.assertIn("Zen Kitchen", [row["title"] for row in result])

    # #22 Update current IDP
    def test_UT50_update_current_idp_with_valid_change(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen", "CURRENT")
        controller = UpdateProjectController()

        # Act
        ok, result = controller.update_project(
            self.designer, project_id, self.project_data(title="Zen Kitchen Plus"))

        # Assert
        self.assertTrue(ok)
        _, project = self.view_record(project_id)
        self.assertEqual(project["title"], "Zen Kitchen Plus")

    def test_UT51_title_emptied(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen", "CURRENT")
        controller = UpdateProjectController()

        # Act
        ok, result = controller.update_project(self.designer, project_id, self.project_data(title=""))

        # Assert
        self.assertFalse(ok)
        _, project = self.view_record(project_id)
        self.assertEqual(project["title"], "Zen Kitchen")

    # #23 Delete current IDP
    def test_UT52_delete_existing_current_idp(self):
        # Arrange
        project_id = self.new_project("Zen Kitchen", "CURRENT")
        controller = DeleteProjectController()

        # Act
        ok, result = controller.delete_project(self.designer, project_id)

        # Assert
        self.assertTrue(ok)
        view_ok, _ = self.view_record(project_id)
        self.assertFalse(view_ok)

    def test_UT53_delete_idp_that_does_not_exist(self):
        # Arrange
        controller = DeleteProjectController()

        # Act
        ok, result = controller.delete_project(self.designer, 9999)

        # Assert
        self.assertFalse(ok)

    # #24 Search current IDPs
    def test_UT54_search_returns_current_idps_only(self):
        # Arrange
        self.new_project("Bright Kitchen", "CURRENT")
        self.new_project("Compact Kitchen", "CURRENT")
        self.new_project("Classic Kitchen", "PAST")
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("kitchen", "CURRENT")

        # Assert
        self.assertTrue(ok)
        self.assertEqual({row["title"] for row in result}, {"Bright Kitchen", "Compact Kitchen"})

    def test_UT55_search_current_with_no_match(self):
        # Arrange
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("zzz", "CURRENT")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)

    # #25 Create past IDP
    def test_UT56_create_past_idp_with_valid_details(self):
        # Arrange
        controller = CreateProjectController()

        # Act
        ok, result = controller.create_project(self.designer, self.project_data("Old Condo", "PAST"))

        # Assert
        self.assertTrue(ok)
        project = db.one("SELECT * FROM projects WHERE title='Old Condo'")
        self.assertEqual(project["status"], "PAST")

    def test_UT57_past_idp_title_empty(self):
        # Arrange
        controller = CreateProjectController()
        before = self.count_projects()

        # Act
        ok, result = controller.create_project(self.designer, self.project_data("", "PAST"))

        # Assert
        self.assertFalse(ok)
        self.assertEqual(self.count_projects(), before)

    # #26 View past IDPs
    def test_UT58_view_past_idps_only(self):
        # Arrange
        controller = ViewProjectController()

        # Act
        ok, result = controller.view_projects("PAST")

        # Assert
        self.assertTrue(ok)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(row["status"] == "PAST" for row in result))

    def test_UT59_new_past_idp_appears_only_in_past_list(self):
        # Arrange
        self.new_project("Old Condo", "PAST")
        controller = ViewProjectController()

        # Act
        _, past = controller.view_projects("PAST")
        _, current = controller.view_projects("CURRENT")

        # Assert
        self.assertIn("Old Condo", [row["title"] for row in past])
        self.assertNotIn("Old Condo", [row["title"] for row in current])

    # #27 Update past IDP
    def test_UT60_update_past_idp_with_valid_change(self):
        # Arrange
        project_id = self.new_project("Old Condo", "PAST")
        controller = UpdateProjectController()

        # Act
        ok, result = controller.update_project(
            self.designer, project_id,
            self.project_data("Old Condo", "PAST", description="Updated completion notes"))

        # Assert
        self.assertTrue(ok)
        _, project = self.view_record(project_id)
        self.assertEqual(project["description"], "Updated completion notes")

    def test_UT61_update_idp_that_does_not_exist(self):
        # Arrange
        controller = UpdateProjectController()

        # Act
        ok, result = controller.update_project(self.designer, 9999, self.project_data())

        # Assert
        self.assertFalse(ok)

    # #28 Delete past IDP
    def test_UT62_delete_existing_past_idp(self):
        # Arrange
        project_id = self.new_project("Old Condo", "PAST")
        controller = DeleteProjectController()

        # Act
        ok, result = controller.delete_project(self.designer, project_id)

        # Assert
        self.assertTrue(ok)
        view_ok, _ = self.view_record(project_id)
        self.assertFalse(view_ok)

    def test_UT63_delete_past_idp_that_does_not_exist(self):
        # Arrange
        controller = DeleteProjectController()

        # Act
        ok, result = controller.delete_project(self.designer, 9999)

        # Assert
        self.assertFalse(ok)

    # #29 Search past IDPs
    def test_UT64_search_returns_past_idps_only(self):
        # Arrange
        self.new_project("City Condo", "CURRENT")
        self.new_project("Garden Condo", "PAST")
        self.new_project("Lake Condo", "PAST")
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("condo", "PAST")

        # Assert
        self.assertTrue(ok)
        self.assertEqual({row["title"] for row in result}, {"Garden Condo", "Lake Condo"})

    def test_UT65_search_past_with_no_match(self):
        # Arrange
        controller = SearchProjectController()

        # Act
        ok, result = controller.search_projects("zzz", "PAST")

        # Assert
        self.assertTrue(ok)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()