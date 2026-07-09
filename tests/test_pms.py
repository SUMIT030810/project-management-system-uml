"""
Unit tests for the Project Management System.
Run with:  python3 -m unittest discover -s tests -v   (from project root, with src on PYTHONPATH)
or simply: cd tests && python3 test_pms.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest
from datetime import date
from pms import (
    Employee, Client, WebDevelopmentProject, MobileAppProject,
    DataScienceProject, ProjectStage, ProjectStatus, PaymentStatus, Company
)


class TestEmployeeAndClient(unittest.TestCase):
    def test_employee_creation(self):
        e = Employee("Test User", "Tester", ["QA"])
        self.assertEqual(e.name, "Test User")
        self.assertIn("QA", e.skills)
        self.assertTrue(e.employee_id.startswith("EMP-"))

    def test_client_tracks_projects(self):
        c = Client("John Doe", "john@doe.com", "Doe Inc")
        self.assertEqual(len(c.projects), 0)
        p = WebDevelopmentProject("Test Site", c, 1000, date(2026, 12, 1))
        self.assertEqual(len(c.projects), 1)
        self.assertIs(c.projects[0], p)


class TestProjectLifecycle(unittest.TestCase):
    def setUp(self):
        self.client = Client("Jane Roe", "jane@roe.com", "Roe LLC")
        self.project = WebDevelopmentProject("Test Portal", self.client, 5000, date(2026, 12, 1))

    def test_initial_stage_is_requirement_feasibility(self):
        self.assertEqual(self.project.tracker.current_stage, ProjectStage.REQUIREMENT_FEASIBILITY)

    def test_advance_stage_moves_forward(self):
        self.project.advance_stage()
        self.assertEqual(self.project.tracker.current_stage, ProjectStage.TESTING)

    def test_advance_stage_stops_at_maintenance(self):
        for _ in range(5):
            self.project.advance_stage()
        self.assertEqual(self.project.tracker.current_stage, ProjectStage.MAINTENANCE)

    def test_status_completed_after_reaching_maintenance(self):
        for _ in range(3):
            self.project.advance_stage()
        self.assertEqual(self.project._status, ProjectStatus.COMPLETED)


class TestAssignmentAndFeedback(unittest.TestCase):
    def setUp(self):
        self.client = Client("Sam Lee", "sam@lee.com", "Lee Corp")
        self.project = WebDevelopmentProject("Sam's Site", self.client, 3000, date(2026, 12, 1))
        self.emp = Employee("Priya Singh", "Developer", ["Python"])

    def test_assign_employee_creates_assignment(self):
        assignment = self.project.assign_employee(self.emp, "Developer")
        self.assertEqual(len(self.project._assignments), 1)
        self.assertIs(assignment.employee, self.emp)

    def test_add_feedback_uses_current_stage(self):
        self.project.add_feedback("Looks good", 5)
        self.assertEqual(len(self.project._feedbacks), 1)

    def test_feedback_rating_is_clamped(self):
        from pms import Feedback
        fb = Feedback(ProjectStage.TESTING, "great", 10)
        self.assertEqual(fb._rating, 5)
        fb2 = Feedback(ProjectStage.TESTING, "bad", -3)
        self.assertEqual(fb2._rating, 1)


class TestBilling(unittest.TestCase):
    def test_web_project_billing_is_flat(self):
        client = Client("A", "a@a.com", "A Inc")
        p = WebDevelopmentProject("P1", client, 1000, date(2026, 12, 1))
        self.assertEqual(p.calculate_billing(), 1000)

    def test_mobile_project_billing_surcharge(self):
        client = Client("B", "b@b.com", "B Inc")
        p = MobileAppProject("P2", client, 1000, date(2026, 12, 1), platforms=["Android", "iOS"])
        # 1 extra platform => +10%
        self.assertEqual(p.calculate_billing(), 1100)

    def test_data_science_large_dataset_surcharge(self):
        client = Client("C", "c@c.com", "C Inc")
        p = DataScienceProject("P3", client, 2000, date(2026, 12, 1), dataset_size_gb=100)
        self.assertEqual(p.calculate_billing(), 2500)

    def test_payment_status_transitions(self):
        client = Client("D", "d@d.com", "D Inc")
        p = WebDevelopmentProject("P4", client, 1000, date(2026, 12, 1))
        self.assertEqual(p.billing.status, PaymentStatus.PENDING)
        p.billing.record_payment(500)
        self.assertEqual(p.billing.status, PaymentStatus.PARTIALLY_PAID)
        p.billing.record_payment(500)
        self.assertEqual(p.billing.status, PaymentStatus.PAID)


class TestCompany(unittest.TestCase):
    def test_company_registers_everything(self):
        company = Company("TestCo")
        emp = Employee("E", "Dev", ["Python"])
        client = Client("Cl", "cl@cl.com", "ClCo")
        company.hire_employee(emp)
        company.onboard_client(client)
        proj = WebDevelopmentProject("Proj", client, 1000, date(2026, 12, 1))
        company.register_project(proj)
        self.assertEqual(len(company.employees), 1)
        self.assertEqual(len(company.projects), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
